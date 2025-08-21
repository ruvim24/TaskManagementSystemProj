import os

from celery.schedules import crontab

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')

app = Celery('proj')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'top-20-tasks-report-every-week': {
        'task': 'apps.tasks.tasks.top_user_tasks',
        'schedule': crontab(minute='30', hour='8', day_of_week='1-5')
    },
}
app.conf.timezone = 'UTC'
