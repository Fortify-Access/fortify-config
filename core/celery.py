from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'update_inbounds_every_2_minutes': {
        'task': 'inbounds_updater',  
        'schedule': crontab(minute='*/2'),
    },
    'check_expirations_every_5_minutes': {
        'task': 'expirations_checker',  
        'schedule': crontab(minute='*/5'),
    },
} 
