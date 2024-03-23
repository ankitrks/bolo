# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-03-30 12:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_user', '0075_auto_20200328_1853'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='invited_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='is_invited',
            field=models.BooleanField(default=False),
        ),
    ]
