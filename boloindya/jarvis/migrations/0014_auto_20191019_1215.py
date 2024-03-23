# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-10-19 12:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jarvis', '0013_auto_20191017_1444'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pushnotification',
            name='notification_type',
            field=models.CharField(blank=True, choices=[('0', 'Particular video page'), ('1', 'Particular user'), ('2', 'Particular category'), ('3', 'Particular hashtag'), ('4', 'Announcements')], default='4', max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='pushnotification',
            name='user_group',
            field=models.CharField(blank=True, choices=[('0', 'All'), ('1', 'Signed up but never played a video'), ('2', 'Signed up but no opening of app since 24 hours'), ('3', 'Signed up but no opening of app since 72 hours '), ('4', 'Never created a video')], default='0', max_length=10, null=True),
        ),
    ]
