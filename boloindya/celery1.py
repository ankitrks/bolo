from __future__ import absolute_import, unicode_literals
from celery import Celery

app = Celery('boloindya',
             broker='redis://localhost:6379',
             backend='redis://localhost:6379',
             include=['tasks'])

if __name__ == '__main__':
    app.start()