from django.contrib.auth.models import User
from django.db import models


class StatusEnum(models.TextChoices):
    OPEN = 'open'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    ARCHIVED = 'archived'


class AttachmentStatus(models.TextChoices):
    IN_PENDING = "in_pending"
    UPLOADED = "uploaded"
    CANCELLED = "cancelled"
    REMOVED = "removed"


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(choices=StatusEnum.choices, max_length=20, default=StatusEnum.OPEN, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='tasks')

    def __str__(self):
        return self.title


class Comment(models.Model):
    content = models.TextField(max_length=250)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')


class TimeLog(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='time_logs')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)


class Attachment(models.Model):
    file_name = models.CharField(max_length=500, default="unknown_file_name")
    pre_assigned_url = models.URLField(max_length=1000, default="")
    url = models.URLField(max_length=1000, default="", null=True, blank=True)
    status = models.CharField(choices=AttachmentStatus.choices, max_length=20,
                              default=AttachmentStatus.IN_PENDING, db_index=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
