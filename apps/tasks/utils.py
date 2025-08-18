from celery import shared_task
from django.core.mail import send_mail

from apps.tasks.models import Task


@shared_task
def task_completed_email(task_id):
    task = Task.objects.get(id=task_id)
    if task is None:
        return
    user_to_notify = task.user
    if user_to_notify is None or user_to_notify.email is None:
        return
    user_email = user_to_notify.email

    send_mail(
        f'Subject: Task completed: {task.title}',
        f'Hello {user_to_notify.username} \n\nTask you are assigned was set as completed\n\nTask: {task.title}\nDescription: {task.description}\nStatus: {task.status}\n',
        'expeditor@exemplu.com',
        [f'{user_email}'],
        fail_silently=False,
    )


@shared_task
def task_commented_email(task_id, comment):
    print("Sending email about new comment on task...")
    task = Task.objects.get(id=task_id)
    if task is None:
        return
    user_to_notify = task.user
    if user_to_notify is None or user_to_notify.email is None:
        return
    user_email = user_to_notify.email

    send_mail(
        f'Subject: Comment add to task: {task.title}',
        f'Hello {user_to_notify.username} \n\nA new comment was added to task you are assigned.\n\nTask: {task.title}\nDescription: {task.description}\nStatus: {task.status}\nNew Comment: {comment}',
        'expeditor@exemplu.com',
        [f'{user_email}'],
        fail_silently=False,
    )

    print("Email sent to user about new comment on task...")


@shared_task
def user_assigned_to_task_email(task_id):
    task = Task.objects.get(id=task_id)
    if task is None:
        return
    user_to_notify = task.user
    if user_to_notify is None or user_to_notify.email is None:
        return
    user_email = user_to_notify.email

    send_mail(
        f'Subject: You have been assigned a new task: {task.title}',
        f'Hello {user_to_notify.username} \n\nThis message is to inform you that you have been assigned to a new task. The task details are as follows:\n\nTask: {task.title}\nDescription: {task.description}\nStatus: {task.status}\nCreated At: {task.created_at}',
        'expeditor@exemplu.com',
        [f'{user_email}'],
        fail_silently=False,
    )
