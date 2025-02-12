# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('forum_topic_notification', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topicnotification',
            name='user',
            field=models.ForeignKey(related_name='st_topic_notifications', to=settings.AUTH_USER_MODEL),
        ),
    ]
