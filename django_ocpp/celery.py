import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_ocpp.settings')

app = Celery('django_ocpp')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
