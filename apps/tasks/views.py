from datetime import datetime

from django.db.models import Sum
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404, ListAPIView, GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED

from .filters import TaskFilter
from .models import Task, StatusEnum, Comment, TimeLog
from .serializers import (TaskDetailsSerializer, AssignUserSerializer, AddCommentToTaskSerializer, CommentSerializer,
                          TasksSerializer, TimeLogSerializer, TaskDurationSerializer, LastMonthDurationSerializer)


# Create your views here.

class TaskDetailsView(viewsets.ModelViewSet):
    serializer_class = TaskDetailsSerializer
    queryset = Task.objects.all()

    get_serializer_class = lambda self: self.serializer_class

    @action(detail=True, methods=['put'], serializer_class=AssignUserSerializer, url_path='assign-user')
    def assign_user(self, request, *args, **kwargs):
        task = self.get_object()
        serializer = self.get_serializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        task.user_assigned_to_task_email()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'], serializer_class=NotImplemented)
    def complete(self, request, *args, **kwargs):
        task = self.get_object()
        task.status = StatusEnum.COMPLETED
        task.save()
        task.task_completed_email()
        return Response({'message': f"Task: f{task.title} completed succesefully"}, status=HTTP_200_OK)

    @action(detail=True, methods=['post'], serializer_class=AddCommentToTaskSerializer)
    def comment(self, request: Request, pk: int) -> Response:
        task = get_object_or_404(Task, id=pk)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_comment = Comment(content=serializer.data['comment'], task=task)
        new_comment.save()
        task.task_commented_email(new_comment.content)
        return Response({'comment_id': f"{new_comment.id}"}, status=HTTP_201_CREATED)

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
            .exists())

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
        time_logs = self.get_object().time_logs.filter(duration__isnull=False)
        logs_duration = time_logs.aggregate(Sum('duration'))['duration__sum']
        logs_duration_in_hours = round(logs_duration / 60, 1)

        return Response({'Total logged time in hours': logs_duration_in_hours}, status=HTTP_200_OK)


class LastMontLoggedTimeDurationView(GenericAPIView):
    serializer_class = LastMonthDurationSerializer

    def get(self, request: Request) -> Response:
        user_id = request.user.id
        time_logs = TimeLog.objects.filter(
            task__user_id=user_id,
            start_time__month=timezone.now().month,
            duration__isnull=False)

        if not time_logs:
            return Response({'message': 'No time logs found'}, status=HTTP_200_OK)

        logs_duration = time_logs.aggregate(Sum('duration'))['duration__sum']
        logs_duration_in_hours = round(logs_duration / 60, 1)

        return Response({'Total logged time in hours for last month': logs_duration_in_hours}, status=HTTP_200_OK)


class TasksListDurationView(GenericAPIView):
    serializer_class = TaskDurationSerializer

    def get(self, request: Request) -> Response:
        tasks = Task.objects.all().filter(time_logs__duration__isnull=False).annotate(
            task_duration=Sum('time_logs__duration'))

        return Response(self.get_serializer(tasks, many=True).data, status=HTTP_200_OK)


class TopTasksLastMonthView(GenericAPIView):
    serializer_class = TaskDurationSerializer

    def get(self, request: Request) -> Response:
        top_tasks = (Task.objects
                     .filter(time_logs__duration__isnull=False,
                             time_logs__start_time__month=timezone.now().month)
                     .annotate(task_duration=Sum('time_logs__duration'))
                     .order_by('-task_duration')[:20])

        return Response(self.get_serializer(top_tasks, many=True).data, status=200)


class TaskListDetailsView(ListAPIView):
    serializer_class = TasksSerializer
    filterset_class = TaskFilter
    search_fields = ['title', 'description']
    ordering = ('-id',)
    ordering_fields = ('id', 'title', 'description', 'status', 'created_at')

    def get_serializer_class(self):
        return self.serializer_class

    def get_queryset(self):
        return Task.objects.all()
