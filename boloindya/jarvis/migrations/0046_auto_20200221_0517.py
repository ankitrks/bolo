# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-02-21 05:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jarvis', '0045_auto_20200221_0203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dashboardmetrics',
            name='metrics_slab',
            field=models.CharField(blank=True, choices=[('0', '5 to 24'), ('1', '25 to 59'), ('2', '60 or more'), ('3', 'Likes'), ('4', 'Comments'), ('5', 'Shares'), ('6', 'Organic'), ('7', 'Paid'), ('t', 'Total')], default=None, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='dashboardmetricsjarvis',
            name='metrics_slab',
            field=models.CharField(blank=True, choices=[('0', '5 to 24'), ('1', '25 to 59'), ('2', '60 or more'), ('3', 'Likes'), ('4', 'Comments'), ('5', 'Shares'), ('6', 'Organic'), ('7', 'Paid'), ('t', 'Total')], default=None, max_length=10, null=True),
        ),
    ]
