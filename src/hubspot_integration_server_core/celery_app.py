import os

from celery import Celery
from flask import Flask

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=os.getenv('CELERY_BROKER_URL'),
    )
    celery.conf.update(app.config)
    return celery
