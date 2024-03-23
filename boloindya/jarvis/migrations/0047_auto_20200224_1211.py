# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-02-24 12:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jarvis', '0046_auto_20200221_0517'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dashboardmetrics',
            name='metrics_slab',
            field=models.CharField(blank=True, choices=[('0', '5 to 24'), ('1', '25 to 59'), ('2', '60 or more'), ('3', 'Likes'), ('4', 'Comments'), ('5', 'Shares'), ('6', 'Organic'), ('7', 'Paid'), ('t', 'Total'), ('10', 'Less than 5')], default=None, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='dashboardmetricsjarvis',
            name='metrics_slab',
            field=models.CharField(blank=True, choices=[('0', '5 to 24'), ('1', '25 to 59'), ('2', '60 or more'), ('3', 'Likes'), ('4', 'Comments'), ('5', 'Shares'), ('6', 'Organic'), ('7', 'Paid'), ('t', 'Total'), ('10', 'Less than 5')], default=None, max_length=10, null=True),
        ),
    ]
