# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-10-04 13:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drf_spirit', '0017_auto_20190923_1632'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyActiveUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_month_year', models.CharField(max_length=250, null=True, verbose_name='day_month_year')),
                ('frequency', models.PositiveIntegerField(default=0, editable=False, verbose_name='frequency')),
            ],
        ),
        migrations.CreateModel(
            name='HourlyActiveUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_week', models.CharField(max_length=250, null=True, verbose_name='day_week')),
                ('hour_week', models.CharField(max_length=250, null=True, verbose_name='hour_week')),
                ('frequency', models.PositiveIntegerField(default=0, editable=False, verbose_name='frequency')),
            ],
        ),
        migrations.CreateModel(
            name='MonthlyActiveUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.CharField(max_length=250, null=True, verbose_name='month')),
                ('frequency', models.PositiveIntegerField(default=0, editable=False, verbose_name='frequency')),
            ],
        ),
        migrations.CreateModel(
            name='UserTimeRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(blank=True, db_index=True, max_length=250, null=True, verbose_name='user')),
                ('timestamp', models.DateTimeField(null=True, verbose_name='timestamp')),
            ],
        ),
    ]
