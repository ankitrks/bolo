# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-10-26 23:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_user', '0052_auto_20191025_1638'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='is_business',
            field=models.BooleanField(default=False, verbose_name='Is Business'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='is_popular',
            field=models.BooleanField(default=False, verbose_name='Is Popular'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='language',
            field=models.CharField(blank=True, choices=[('1', 'English'), ('2', 'Hindi'), ('3', 'Tamil'), ('4', 'Telgu'), ('5', 'Bengali'), ('6', 'Kannada')], default='1', max_length=10, null=True),
        ),
    ]
