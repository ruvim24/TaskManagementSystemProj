from rest_framework import serializers

from apps.tasks.models import Task, Comment
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
    user_id = serializers.IntegerField()


class AddCommentToTaskSerializer(serializers.Serializer):
    comment = serializers.CharField(max_length=250)
