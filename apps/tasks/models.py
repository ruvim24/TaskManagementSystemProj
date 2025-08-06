from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import models


# Create your models here.

class StatusEnum(models.TextChoices):
    OPEN = 'open'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    ARCHIVED = 'archived'


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(choices=StatusEnum.choices, max_length=20, default=StatusEnum.OPEN, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='tasks')

    def task_completed_email(self):
        user_to_notify = self.user
        user_email = user_to_notify.email

        send_mail(
            f'Subject: Task completed: {self.title}',
            f'Hello {user_to_notify.username} \n\nTask you are assigned was set as completed\n\nTask: {self.title}\nDescription: {self.description}\nStatus: {self.status}\n',
            'expeditor@exemplu.com',
            [f'{user_email}'],
            fail_silently=False,
        )

    def task_commented_email(self, comment):
        user_to_notify = self.user
        user_email = user_to_notify.email

        send_mail(
            f'Subject: Comment add to task: {self.title}',
            f'Hello {user_to_notify.username} \n\nA new comment was added to task you are assigned.\n\nTask: {self.title}\nDescription: {self.description}\nStatus: {self.status}\nNew Comment: {comment}',
            'expeditor@exemplu.com',
            [f'{user_email}'],
            fail_silently=False,
        )

    def user_assigned_to_task_email(self):
        user_to_notify = self.user
        user_email = user_to_notify.email

        send_mail(
            f'Subject: You have been assigned a new task: {self.title}',
            f'Hello {user_to_notify.username} \n\nThis message is to inform you that you have been assigned to a new task. The task details are as follows:\n\nTask: {self.title}\nDescription: {self.description}\nStatus: {self.status}\nCreated At: {self.created_at}',
            'expeditor@exemplu.com',
            [f'{user_email}'],
            fail_silently=False,
        )


def __str__(self):
    return self.title


class Comment(models.Model):
    content = models.TextField(max_length=250)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
