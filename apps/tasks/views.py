from django.contrib.auth.models import User
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.generics import GenericAPIView, get_object_or_404, ListAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED

from .filters import TaskFilter
from .models import Task, StatusEnum, Comment
from .serializers import (TaskDetailsSerializer, TasksSerializer,
                          AssignUserSerializer, AddCommentToTaskSerializer, CommentSerializer)


# Create your views here.


class TaskDetailsView(GenericAPIView):
    serializer_class = TaskDetailsSerializer

    def get(self, request: Request, pk: int) -> Response:
        task = get_object_or_404(Task, id=pk)
        return Response(self.serializer_class(task).data, status=HTTP_200_OK)


class CreateTaskView(GenericAPIView):
    serializer_class = TaskDetailsSerializer

    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(id=request.user.id)
        task = Task(**serializer.validated_data, user=user)
        task.save()
        return Response(serializer.data, status=HTTP_201_CREATED)


class TaskListDetailsView(ListAPIView):
    serializer_class = TaskDetailsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter

    def get_queryset(self):
        return Task.objects.all()


class TaskListView(ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TasksSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['title']
    filterset_class = TaskFilter


class AssignUserToTask(UpdateAPIView):
    serializer_class = AssignUserSerializer

    def update(self, request, *args, **kwargs):
        task = Task.objects.get(id=kwargs['pk'])
        user = User.objects.get(id=request.data['user_id'])

        task.user = user
        task.save()
        user_assigned_to_task_email(task)
        return (Response({'message': f"User: f{user.username} assigned succesefully to task: f{task.title}"},
                         status=HTTP_200_OK))


class CompleteTaskView(UpdateAPIView):
    def update(self, request, *args, **kwargs):
        task = Task.objects.get(id=kwargs['pk'])
        task.status = StatusEnum.COMPLETED.value
        task.save()
        task_completed_email(task)
        return Response({'message': f"Task: f{task.title} completed succesefully"}, status=HTTP_200_OK)


class RemoveTaskView(DestroyAPIView):
    queryset = Task.objects.all()


class AddCommentToTask(GenericAPIView):
    serializer_class = AddCommentToTaskSerializer

    def post(self, request: Request, pk: int) -> Response:
        task = get_object_or_404(Task, id=pk)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_comment = Comment(content=serializer.data['comment'], task=task)
        new_comment.save()
        task_commented_email(task, new_comment.content)
        return Response({'comment_id': f"{new_comment.id}"}, status=HTTP_201_CREATED)


class TaskCommentsView(GenericAPIView):
    serializer_class = CommentSerializer

    def get(self, request: Request, pk: int) -> Response:
        task = get_object_or_404(Task, id=pk)
        comments = Comment.objects.filter(task=task)
        return Response(self.serializer_class(comments, many=True).data, status=HTTP_200_OK)


def user_assigned_to_task_email(task):
    user_to_notify = task.user
    user_email = user_to_notify.email

    if user_email is None or '@' not in user_email:
        print(f"User: {user_to_notify.first_name} has not and email registred or is not valid")
        return
    else:
        send_mail(
            f'Subject: You have been assigned a new task: {task.title}',
            f'Hello {user_to_notify.username} \n\nThis message is to inform you that you have been assigned to a new task. The task details are as follows:\n\nTask: {task.title}\nDescription: {task.description}\nStatus: {task.status}\nCreated At: {task.created_at}',
            'expeditor@exemplu.com',
            [f'{user_email}'],
            fail_silently=False,
        )


def task_commented_email(task, comment):
    user_to_notify = task.user
    user_email = user_to_notify.email

    if user_email is None or '@' not in user_email:
        print(f"User: {user_to_notify.first_name} has not and email registred or is not valid")
        return
    else:
        send_mail(
            f'Subject: Comment add to task: {task.title}',
            f'Hello {user_to_notify.username} \n\nA new comment was added to task you are assigned.\n\nTask: {task.title}\nDescription: {task.description}\nStatus: {task.status}\nNew Comment: {comment}',
            'expeditor@exemplu.com',
            [f'{user_email}'],
            fail_silently=False,
        )


def task_completed_email(task):
    user_to_notify = task.user
    user_email = user_to_notify.email

    if user_email is None or '@' not in user_email:
        print(f"User: {user_to_notify.first_name} has not and email registered or is not valid")
        return
    else:
        send_mail(
            f'Subject: Task completed: {task.title}',
            f'Hello {user_to_notify.username} \n\nTask you are assigned was set as completed\n\nTask: {task.title}\nDescription: {task.description}\nStatus: {task.status}\n',
            'expeditor@exemplu.com',
            [f'{user_email}'],
            fail_silently=False,
        )
