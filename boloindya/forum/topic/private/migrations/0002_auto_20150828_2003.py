# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('forum_topic_private', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topicprivate',
            name='user',
            field=models.ForeignKey(related_name='st_topics_private', to=settings.AUTH_USER_MODEL),
        ),
    ]
