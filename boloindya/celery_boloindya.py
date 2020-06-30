from __future__ import absolute_import, unicode_literals
from celery import Celery
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings_local")
app = Celery('boloindya',
             # broker='sqs://AKIAZNK4CM5CS5K7QHHW:Y5BMVprF2FGjaEbU8HlH8AH5cbopn1SGCdlc54Wb@', # 'redis://localhost:6379',
             broker='redis://boloindya.nf4tvd.ng.0001.aps1.cache.amazonaws.com:6379',
             backend='redis://boloindya.nf4tvd.ng.0001.aps1.cache.amazonaws.com:6379',
             #broker = 'redis://localhost:6379',
             #backend = 'redis://localhost:6379',
             include=['tasks'])

if __name__ == '__main__':
    app.start()
