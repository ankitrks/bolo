# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-02-05 17:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jarvis', '0036_dashboardmetricsjarvis'),
    ]

    operations = [
        migrations.AddField(
            model_name='pushnotification',
            name='particular_user_id',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='particular_user_id'),
        ),
    ]
