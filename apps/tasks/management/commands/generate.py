import random

from django.core.management.base import BaseCommand, CommandError

from apps.tasks.models import Task, TimeLog


class Command(BaseCommand):
    help = 'Generates in db tasks and time logs'

    def handle(self, *args, **options):

        try:
            task_to_create = []
            for i in range(25000):
                task_to_create.append(Task(title=f'Task {i}', description=f'Description {i}', status='open'))
            Task.objects.bulk_create(task_to_create)

            time_logs_to_create = []
            for i in range(50000):
                time_logs_to_create.append(TimeLog(start_time=f'2025-07-22T10:30:00Z', end_time=f'2025-07-22T10:33:00Z',
                                                   duration=60, task_id=random.randint(1, 25000)))
            TimeLog.objects.bulk_create(time_logs_to_create)

            self.stdout.write(
                self.style.SUCCESS('Successfully generated tasks and time logs in db')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR('Some errors occurred at generation tasks and time logs in db.')
            )
            raise CommandError(f'Error: {e}')
