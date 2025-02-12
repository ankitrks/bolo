# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-02-18 14:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jarvis', '0040_pushnotificationuser_device'),
    ]

    operations = [
        migrations.AddField(
            model_name='fcmdevice',
            name='current_version',
            field=models.CharField(blank=True, default='', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='fcmdevice',
            name='device_model',
            field=models.CharField(blank=True, default='', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='fcmdevice',
            name='manufacturer',
            field=models.CharField(blank=True, default='', max_length=10, null=True),
        ),
    ]
