import logging

from django.dispatch import receiver

from apps.tasks.models import Task
from .signals import task_completed, task_commented, task_assigned
from .utils import task_completed_email, task_commented_email, user_assigned_to_task_email

logger = logging.getLogger(__name__)


@receiver(signal=task_completed, sender=Task)
def task_completed_email_handler(sender, instance, **kwargs):
    logger.info("Task completed email handler")
    task_completed_email.delay(instance.id)


@receiver(signal=task_commented, sender=Task)
def task_commented_email_handler(sender, instance, **kwargs):
    logger.info("Task commented email handler")
    comment = kwargs.get("comment", "")
    task_commented_email.delay(instance.id, comment=comment)


@receiver(signal=task_assigned, sender=Task)
def task_assigned_email_handler(sender, instance, **kwargs):
    logger.info("Task assigned email handler")
    user_assigned_to_task_email.delay(instance.id)
