from django_elasticsearch_dsl.registries import registry
from django_elasticsearch_dsl import Document, fields

from apps.tasks.models import Task, Comment


@registry.register_document
class TaskDocument(Document):
    class Index:
        name = 'tasks'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Task
        fields = [
            'title',
            'description',
            'status',
        ]

@registry.register_document
class CommentDocument(Document):
    class Index:
        name = 'content'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Comment
        fields = [
            'content',
        ]
