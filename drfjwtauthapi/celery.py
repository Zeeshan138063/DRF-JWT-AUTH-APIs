import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drfjwtauthapi.settings')

app = Celery('drfjwtauthapi')
# app = Celery('drfjwtauthapi',backend='amqp://localhost',broker='amqp://localhost')
# app = Celery('drfjwtauthapi', backend='rpc://', broker='amqp://jimmy:jimmy123@localhost/jimmy_vhost')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
