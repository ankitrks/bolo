# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-10-18 21:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_user', '0049_videoplaytime_timestamp'),
    ]

    operations = [
        migrations.AddField(
            model_name='videocompleterate',
            name='timestamp',
            field=models.DateTimeField(null=True, verbose_name='timestamp'),
        ),
    ]
