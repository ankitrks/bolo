# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-06-06 12:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_user', '0021_auto_20190524_1449'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_test_user',
            field=models.BooleanField(default=False),
        ),
    ]
