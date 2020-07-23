# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-07-09 13:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_user', '0091_auto_20200708_2008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='language',
            field=models.CharField(blank=True, choices=[(b'0', b'All'), (b'1', b'English'), (b'2', b'Hindi'), (b'3', b'Tamil'), (b'4', b'Telugu'), (b'5', b'Bengali'), (b'6', b'Kannada'), (b'7', b'Malayalam'), (b'8', b'Gujarati'), (b'9', b'Marathi'), (b'10', b'Punjabi'), (b'11', b'Odia'), (b'12', b'Bhojpuri'), (b'13', b'Haryanvi'), (b'14', b'Sinhala')], db_index=True, default='1', max_length=10, null=True),
        ),
    ]
