from datetime import datetime, timedelta

from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone
from elasticsearch.dsl.query import MultiMatch
from minio import Minio
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED
from rest_framework.views import APIView

from DjangoProject.settings import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY
from . import signals
from .documents import TaskDocument, CommentDocument
from .filters import TaskFilter
from .models import Task, StatusEnum, Comment, TimeLog, Attachment, AttachmentStatus
from .serializers import (
    TaskDetailsSerializer,
    AssignUserSerializer,
    AddCommentToTaskSerializer,
    CommentSerializer,
    TasksSerializer,
    TimeLogSerializer,
    TaskDurationSerializer,
    LastMonthDurationSerializer,
    GetPreassignedUploadUrlSerializer,
    AttachmentSerializer,
    ElasticSearchSerializer
)


# Create your views here.
class TaskDetailsView(viewsets.ModelViewSet):
    serializer_class = TaskDetailsSerializer
    queryset = Task.objects.all()

    @action(detail=True, methods=['put'], serializer_class=AssignUserSerializer, url_path='assign-user')
    def assign_user(self, request, *args, **kwargs):
        task = self.get_object()

        serializer = self.get_serializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        task.user = serializer.validated_data['user']
        task.save()
        signals.task_assigned.send(sender=self.__class__, instance=task)

        return Response(data=f"User: {task.user.username} assigned to task: {task.title} successfully",
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'], serializer_class=NotImplemented)
    def complete(self, request, *args, **kwargs):
        task = self.get_object()
        task.status = StatusEnum.COMPLETED
        task.save()

        signals.task_completed.send(sender=self.__class__, instance=task)

        return Response({'message': f"Task: f{task.title} completed successfully"}, status=HTTP_200_OK)

    @action(detail=True, methods=['post'], serializer_class=AddCommentToTaskSerializer)
    def comment(self, request: Request, pk: int) -> Response:
        task = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_comment = Comment(content=serializer.data['comment'], task=task)
        new_comment.save()

        result = signals.task_commented.send(sender=self.__class__, instance=task, comment=new_comment.content)

        return Response({'comment_id': f"{new_comment.id}", 'result': f"{result}"}, status=HTTP_201_CREATED)

    @action(detail=True, methods=['get'], serializer_class=CommentSerializer)
    def comments(self, request, pk=None):
        task = self.get_object()
        comments = task.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], serializer_class=NotImplemented, url_path='start-timer')
    def start_timer(self, request, pk=None):
        task = self.get_object()

        is_timer_started = (
            task.time_logs.filter(
                start_time__isnull=False,
                end_time__isnull=True)
            .exists()
        )

        if is_timer_started:
            raise ValidationError('Timer already started')

        new_time_log = TimeLog(task=self.get_object(), start_time=datetime.now())
        new_time_log.save()

        return Response({'message': 'Timer started'}, status=HTTP_200_OK)

    @action(detail=True, methods=['put'], serializer_class=NotImplemented, url_path='stop-timer')
    def stop_timer(self, request, pk=None):
        task = self.get_object()

        started_timer: TimeLog = (
            task.time_logs.filter(
                start_time__isnull=False,
                end_time__isnull=True,
                duration__isnull=True)
            .first())

        if started_timer is None:
            raise ValidationError('Timer not started')

        duration = started_timer.start_time - timezone.now()

        started_timer.end_time = datetime.now()
        started_timer.duration = duration.total_seconds() / 60
        started_timer.save()

        return Response(TimeLogSerializer(started_timer).data, status=HTTP_200_OK)

    @action(detail=True, methods=['get'], serializer_class=TimeLogSerializer, url_path='time-logs')
    def time_logs(self, request: Request, pk=None):
        time_logs = self.get_object().time_logs.all()
        self.get_serializer(time_logs, many=True)
        return Response(self.get_serializer(time_logs, many=True).data)

    @action(detail=True, methods=['post'], serializer_class=TimeLogSerializer, url_path='log-time')
    def log_time(self, request: Request, pk=None):
        task = self.get_object()
        data = TimeLogSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        validated_data = data.validated_data

        start_time = validated_data['start_time']
        end_time = validated_data['end_time']
        duration = validated_data['duration']

        if duration == 0 or duration is None:
            duration = (end_time - start_time).total_seconds() / 60

        new_time_log = TimeLog(task=task, start_time=start_time, end_time=end_time, duration=duration)
        new_time_log.save()
        return Response(TimeLogSerializer(new_time_log).data, status=HTTP_201_CREATED)

    @action(detail=True, methods=['get'], serializer_class=NotImplemented, url_path='logged-time-duration')
    def logged_time_duration(self, request: Request, pk=None):

        logs_duration = (
            self.get_object()
            .time_logs
            .filter(duration__isnull=False)
            .aggregate(Sum('duration'))['duration__sum']
        )

        logs_duration_in_hours = round(logs_duration / 60, 1)

        return Response({'Total logged time in hours': logs_duration_in_hours}, status=HTTP_200_OK)

    @action(
        methods=['put'],
        detail=True,
        serializer_class=GetPreassignedUploadUrlSerializer,
        url_path='get-preassigned-url')
    def get_preassigned_url(self, request: Request, pk=None):

        task = self.get_object()
        if task is None:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False
        )

        bucket_name = "files"
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)

        file_name = request.data['file_name']
        try:
            url = client.get_presigned_url(
                bucket_name=bucket_name,
                object_name=file_name,
                expires=timedelta(seconds=300),
                method="PUT"
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        attachment = Attachment.objects.create(pre_assigned_url=url, task=task, file_name=file_name)
        attachment.save()

        return Response(GetPreassignedUploadUrlSerializer(attachment).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], serializer_class=AttachmentSerializer, url_path='attachments')
    def task_attachments_list(self, request: Request, pk: int):
        task = self.get_object()
        attachments = task.attachments
        serializer = self.get_serializer(attachments, many=True)
        return Response(serializer.data, status=HTTP_200_OK)


class LastMontLoggedTimeDurationView(GenericAPIView):
    serializer_class = LastMonthDurationSerializer

    def get(self, request: Request) -> Response:
        user_id = request.user.id

        time_logs = (
            TimeLog.objects
            .filter(
                task__user_id=user_id,
                start_time__month=timezone.now().month,
                duration__isnull=False
            )
        )

        if not time_logs:
            return Response({'message': 'No time logs found'}, status=HTTP_200_OK)

        logs_duration = time_logs.aggregate(Sum('duration'))['duration__sum']
        logs_duration_in_hours = round(logs_duration / 60, 1)

        return Response({'Total logged time in hours for last month': logs_duration_in_hours}, status=HTTP_200_OK)


class TasksListDurationView(GenericAPIView):
    serializer_class = TaskDurationSerializer

    def get(self, request: Request) -> Response:
        tasks = (
            Task.objects.all()
            .filter(time_logs__duration__isnull=False)
            .annotate(task_duration=Sum('time_logs__duration'))
        )

        return Response(self.get_serializer(tasks, many=True).data, status=HTTP_200_OK)


class TopTasksLastMonthView(GenericAPIView):
    serializer_class = TaskDurationSerializer

    def get(self, request: Request) -> Response:
        top_tasks = (
            Task.objects
            .filter(
                time_logs__duration__isnull=False,
                time_logs__start_time__month=timezone.now().month
            )
            .annotate(task_duration=Sum('time_logs__duration'))
            .order_by('-task_duration')[:20]
        )

        return Response(self.get_serializer(top_tasks, many=True).data, status=200)


class TaskListDetailsView(ListAPIView):
    serializer_class = TasksSerializer
    queryset = Task.objects.all()
    filterset_class = TaskFilter
    search_fields = ['title', 'description']
    ordering = ('-id',)
    ordering_fields = ('id', 'title', 'description', 'status', 'created_at')


class UploadFileView(APIView):
    def post(self, request: Request):
        try:
            minio_event = request.data['Records'][0]
            file_key = minio_event['s3']['object']['key']
            bucket_name = minio_event['s3']['bucket']['name']
        except (KeyError, IndexError):
            return Response({'error': 'Invalid MinIO event payload'}, status=status.HTTP_400_BAD_REQUEST)

        attachment = Attachment.objects.get(file_name=file_key)
        if not attachment:
            print(f"Attachment with: {file_key} not found")

        minio_base_url = f"http://{MINIO_ENDPOINT}"
        file_url = f"{minio_base_url}/{bucket_name}/{file_key}"
        attachment.url = file_url
        attachment.status = AttachmentStatus.UPLOADED
        attachment.save()
        print(f"File {file_key} successfully uploaded")

        return Response(status=HTTP_200_OK)


class SearchTasksView(ListAPIView):
    serializer_class = ElasticSearchSerializer

    def get(self, request: Request, *args, **kwargs):
        s = TaskDocument.search()

        query = MultiMatch(
            query=request.query_params.get('search', ''),
            fields=['title', 'description']
        )

        s = s.query(query)
        response = s.execute()

        hits = [hit.to_dict() for hit in response.hits]

        return Response(hits, status=HTTP_200_OK)


class SearchCommentsView(ListAPIView):
    serializer_class = ElasticSearchSerializer

    def get(self, request: Request, *args, **kwargs):
        s = CommentDocument.search()

        query = MultiMatch(
            query=request.query_params.get('search', ''),
            fields=['content']
        )

        s = s.query(query)
        response = s.execute()

        hits = [hit.to_dict() for hit in response.hits]

        return Response(hits, status=HTTP_200_OK)


def profile(request):
    return render(request, 'profile.html')
