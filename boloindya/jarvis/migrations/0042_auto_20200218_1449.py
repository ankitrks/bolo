# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-02-18 14:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jarvis', '0041_auto_20200218_0134'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dashboardmetrics',
            name='metrics',
            field=models.CharField(blank=True, choices=[('0', 'Video Created'), ('1', 'Video Views'), ('2', 'Bolo Actions'), ('3', 'Video Shares'), ('4', 'Video Creators'), ('5', 'Number of Installs'), ('6', 'DAU'), ('7', 'Unique Video Views'), ('8', 'MAU')], default='0', max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='dashboardmetricsjarvis',
            name='metrics',
            field=models.CharField(blank=True, choices=[('0', 'Video Created'), ('1', 'Video Views'), ('2', 'Bolo Actions'), ('3', 'Video Shares'), ('4', 'Video Creators'), ('5', 'Number of Installs'), ('6', 'DAU'), ('7', 'Unique Video Views'), ('8', 'MAU')], default='0', max_length=10, null=True),
        ),
    ]
