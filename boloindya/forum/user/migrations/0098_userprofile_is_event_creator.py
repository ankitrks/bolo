# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-10-24 16:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_user', '0097_userprofile_is_bot_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_event_creator',
            field=models.BooleanField(default=False),
        ),
    ]
