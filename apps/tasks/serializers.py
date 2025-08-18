from django.contrib.auth.models import User
from rest_framework import serializers

from apps.tasks.models import Task, Comment, TimeLog, Attachment
from apps.users.serializers import UserSerializer


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'content')


class TaskDetailsSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'status', 'created_at', 'updated_at', 'user', 'comments')


class TasksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title')


class AssignUserSerializer(serializers.Serializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user')


class AddCommentToTaskSerializer(serializers.Serializer):
    comment = serializers.CharField(max_length=250)


class TimeLogSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M")
    end_time = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M")
    duration = serializers.IntegerField(required=True, min_value=0)

    class Meta:
        model = TimeLog
        fields = ('id', 'start_time', 'end_time', 'duration')


class TaskDurationSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    task_duration = serializers.IntegerField(min_value=0)


class LastMonthDurationSerializer(serializers.Serializer):
    total_hours = serializers.FloatField()


class GetPreassignedUploadUrlSerializer(serializers.ModelSerializer):
    url = serializers.URLField(read_only=True)
    id = serializers.IntegerField(read_only=True)
    task_id = serializers.IntegerField(read_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Attachment
        fields = ['id', 'url', 'file_name', 'status', 'task_id']


class UploadCompletedSerializer(serializers.Serializer):
    attachment_id = serializers.PrimaryKeyRelatedField(queryset=Attachment.objects.all())
    url = serializers.URLField(required=True)


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ('id', 'file_name', 'url')


class ElasticSearchSerializer(serializers.Serializer):
    search = serializers.CharField(
        max_length=1000,
        required=False,
        allow_blank=True
    )
