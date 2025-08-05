from enum import Enum
from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class StatusEnum(Enum):
    OPEN = 'open'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    ARCHIVED = 'archived'


STATUS_CHOICES = [(status.value, status.value) for status in StatusEnum]


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default=StatusEnum.OPEN.value)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='tasks')

    def __str__(self):
        return self.title

class Comment(models.Model):
    content = models.TextField(max_length=250)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')