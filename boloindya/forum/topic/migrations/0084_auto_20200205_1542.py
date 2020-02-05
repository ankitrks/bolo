# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-02-05 15:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_topic', '0083_merge_20200205_1515'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobrequest',
            name='cover_letter',
            field=models.FileField(blank=True, null=True, upload_to='documents/', verbose_name='Upload Cover Letter'),
        ),
        migrations.AlterField(
            model_name='jobrequest',
            name='document',
            field=models.FileField(blank=True, null=True, upload_to='documents/', verbose_name='Upload resume'),
        ),
    ]
