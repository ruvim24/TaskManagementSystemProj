from django.core.management.base import BaseCommand, CommandError

from apps.tasks.factories import TaskFactory, TimeLogFactory


class Command(BaseCommand):
    help = 'Generates in db tasks and time logs'

    def handle(self, *args, **options):

        try:
            TaskFactory.create_batch(25000)
            TimeLogFactory.create_batch(50000)

            self.stdout.write(
                self.style.SUCCESS('Successfully generated tasks and time logs in db')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR('Some errors occurred at generation tasks and time logs in db.')
            )
            raise CommandError(f'Error: {e}')
