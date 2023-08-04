from celery import Celery
from django.conf import settings
from celery.schedules import crontab

app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    'inbounds_updater': {
        'task': 'inbounds.tasks.inbounds_updater',
        'schedule': crontab(minute='*/15'),
    },
}
