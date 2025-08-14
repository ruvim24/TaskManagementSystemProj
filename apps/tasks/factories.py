from datetime import datetime, timedelta

import factory
from django.contrib.auth.models import User

from apps.tasks.models import Task, StatusEnum, Comment, TimeLog
import pytz
from django.utils import timezone


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('name')
    email = factory.Faker('email')
    password = factory.Faker('password')


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    content = factory.Faker('sentence')
    task = factory.SubFactory('apps.tasks.factories.TaskFactory')


class TimeLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TimeLog

    task = factory.SubFactory('apps.tasks.factories.TaskFactory')

    start_time = factory.Faker(
        'date_time_this_year',
        tzinfo=timezone.get_current_timezone()
    )
    end_time = factory.LazyAttribute(
        lambda o: o.start_time + timedelta(hours=4)
    )
    duration = factory.LazyAttribute(
        lambda o: (o.end_time - o.start_time).total_seconds()
    ) if end_time is None else 0


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    title = factory.Faker('name')
    description = factory.Faker('sentence')
    status = factory.Iterator(StatusEnum)
    user = factory.SubFactory(UserFactory)

    created_at = factory.Faker(
        'date_time_this_year',
        tzinfo=timezone.get_current_timezone()
    )
    updated_at = factory.LazyAttribute(
        lambda o: o.created_at + timedelta(minutes=5)
    )
