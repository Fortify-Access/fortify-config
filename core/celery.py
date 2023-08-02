from celery import Celery
from django.conf import settings
from celery.schedules import crontab

app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    'your_periodic_task_name': {
        'task': 'your_app.tasks.your_periodic_task',
        'schedule': crontab(minute='*/15'),  # Replace this with your desired schedule
    },
}
