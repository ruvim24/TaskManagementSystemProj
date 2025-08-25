from celery import shared_task
from django.core.mail import send_mail

from apps.tasks.models import Task


@shared_task
def task_completed_email(task_id):
    task = Task.objects.get(id=task_id)

    task_completed_email_result = {
        'task_id': task_id,
        'email_sent': False,
        'error': None,
    }

    if task is None:
        task_completed_email_result['error'] = 'Task not found'
        return task_completed_email_result

    user_to_notify = task.user
    if user_to_notify is None or user_to_notify.email is None:
        task_completed_email_result['error'] = 'User or user email not found'
        return task_completed_email_result

    user_email = user_to_notify.email

    try:
        result = send_mail(
            f'Subject: Task completed: {task.title}',
            f'Hello {user_to_notify.username} '
            f'\n\nTask you are assigned was set as completed'
            f'\n\nTask: {task.title}'
            f'\nDescription: {task.description}'
            f'\nStatus: {task.status}\n',
            'expeditor@exemplu.com',
            [f'{user_email}'],
            fail_silently=False,
        )

        if result == 1:
            task_completed_email_result['email_sent'] = True
        else:
            task_completed_email_result['error'] = 'Email sending failed'
            task_completed_email_result['email_sent'] = False

    except Exception as e:
        task_completed_email_result['error'] = str(e)
        return task_completed_email_result

    return task_completed_email_result


@shared_task
def task_commented_email(task_id, comment):
    task = Task.objects.get(id=task_id)

    task_commented_email_result = {
        'task_id': task_id,
        'email_sent': False,
        'error': None,
    }
    if task is None:
        task_commented_email_result['error'] = 'Task not found'
        return task_commented_email_result

    user_to_notify = task.user
    if user_to_notify is None or user_to_notify.email is None:
        task_commented_email_result['error'] = 'User or user email not found'
        return task_commented_email_result

    user_email = user_to_notify.email
    try:
        result = send_mail(
            f'Subject: Comment add to task: {task.title}',
            f'Hello {user_to_notify.username} '
            f'\n\nA new comment was added to task you are assigned.'
            f'\n\nTask: {task.title}'
            f'\nDescription: {task.description}'
            f'\nStatus: {task.status}'
            f'\nNew Comment: {comment}',
            'expeditor@exemplu.com',
            [f'{user_email}'],
            fail_silently=False,
        )
        if result == 1:
            task_commented_email_result['email_sent'] = True
        else:
            task_commented_email_result['error'] = 'Email sending failed'
            task_commented_email_result['email_sent'] = False
    except Exception as e:
        task_commented_email_result['error'] = str(e)

    return task_commented_email_result


@shared_task
def user_assigned_to_task_email(task_id):
    task = Task.objects.get(id=task_id)

    user_assigned_to_task_email_result = {
        'task_id': task_id,
        'email_sent': False,
        'error': None,
    }
    if task is None:
        user_assigned_to_task_email_result['error'] = 'Task not found'
        return user_assigned_to_task_email_result

    user_to_notify = task.user
    if user_to_notify is None or user_to_notify.email is None:
        user_assigned_to_task_email_result['error'] = 'User or user email not found'
        return user_assigned_to_task_email_result

    user_email = user_to_notify.email

    try:
        result = send_mail(
            f'Subject: You have been assigned a new task: {task.title}',
            f'Hello {user_to_notify.username} '
            f'\n\nThis message is to inform you that you have been assigned to a new task. '
            f'The task details are as follows:\n\nTask: {task.title}'
            f'\nDescription: {task.description}'
            f'\nStatus: {task.status}'
            f'\nCreated At: {task.created_at}',
            'expeditor@exemplu.com',
            [f'{user_email}'],
            fail_silently=False,
        )
        if result == 1:
            user_assigned_to_task_email_result['email_sent'] = True
        else:
            user_assigned_to_task_email_result['error'] = 'Email sending failed'
    except Exception as e:
        user_assigned_to_task_email_result['error'] = str(e)

    return user_assigned_to_task_email_result
