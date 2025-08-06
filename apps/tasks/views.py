from django_filters.rest_framework import DjangoFilterBackend
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404, ListAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED

from .filters import TaskFilter
from .models import Task, StatusEnum, Comment
from .serializers import (TaskDetailsSerializer, AssignUserSerializer, AddCommentToTaskSerializer, CommentSerializer,
                          TasksSerializer)


# Create your views here.

class TaskDetailsView(viewsets.ModelViewSet):
    serializer_class = TaskDetailsSerializer
    queryset = Task.objects.all()

    @action(detail=True, methods=['put'], serializer_class=AssignUserSerializer)
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


class TaskListDetailsView(ListAPIView):
    serializer_class = TasksSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter

    def get_queryset(self):
        return Task.objects.all()
