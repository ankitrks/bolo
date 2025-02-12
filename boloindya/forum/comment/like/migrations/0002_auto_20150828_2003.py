# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('forum_comment_like', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commentlike',
            name='user',
            field=models.ForeignKey(related_name='st_comment_likes', to=settings.AUTH_USER_MODEL),
        ),
    ]
