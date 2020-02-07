# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-01-24 15:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('forum_topic', '0079_auto_20200124_1243'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobopening',
            name='is_active',
        ),
        migrations.AddField(
            model_name='jobopening',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='jobopening',
            name='expiry_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Expiry date'),
        ),
        migrations.AddField(
            model_name='jobopening',
            name='last_modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='jobopening',
            name='publish_status',
            field=models.CharField(blank=True, choices=[('0', 'Unpublish'), ('1', 'Publish')], max_length=10, null=True, verbose_name='Publish'),
        ),
    ]
