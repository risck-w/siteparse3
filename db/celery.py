from celery import Celery
from settings import celeryconfig


'''
@Celery driver

'''

app = Celery(
    'tasks',
    broker='amqp://admin:admin@116.205.134.152:5672',
    backend='rpc://'
)
app.config_from_object(celeryconfig)

