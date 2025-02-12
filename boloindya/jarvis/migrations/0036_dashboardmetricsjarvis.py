# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-02-05 15:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jarvis', '0035_merge_20200205_1515'),
    ]

    operations = [
        migrations.CreateModel(
            name='DashboardMetricsJarvis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('metrics', models.CharField(blank=True, choices=[('0', 'Video Created'), ('1', 'Video Views'), ('2', 'Bolo Actions'), ('3', 'Video Shares'), ('4', 'Video Creators'), ('5', 'Number of Installs'), ('6', 'Monthly Active Users'), ('7', 'Unique Video Views')], default='0', max_length=10, null=True)),
                ('metrics_slab', models.CharField(blank=True, choices=[('0', '5 to 24'), ('1', '25 to 59'), ('2', '60 or more'), ('3', 'Likes'), ('4', 'Comments'), ('5', 'Shares'), ('6', 'Organic'), ('7', 'Paid'), ('t', 'Total')], default=None, max_length=10, null=True)),
                ('date', models.DateTimeField()),
                ('week_no', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('count', models.PositiveIntegerField(blank=True, default=0, null=True)),
            ],
            options={
                'ordering': ['date'],
            },
        ),
    ]
