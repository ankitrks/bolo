# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-10-07 12:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drf_spirit', '0022_hourlyactiveuser_day_week'),
    ]

    operations = [
        migrations.AddField(
            model_name='hourlyactiveuser',
            name='date_time_field',
            field=models.DateTimeField(null=True, verbose_name='date_time_field'),
        ),
    ]
