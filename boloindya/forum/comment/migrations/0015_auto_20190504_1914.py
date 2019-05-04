# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-04 19:14
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forum_comment', '0014_auto_20190504_1841'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='st_comments', to=settings.AUTH_USER_MODEL),
        ),
    ]
