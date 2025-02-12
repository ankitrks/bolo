# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-08-05 15:58
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum_user', '0025_auto_20190729_1642'),
    ]

    operations = [
        migrations.CreateModel(
            name='AndroidLogs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('logs', models.TextField(blank=True, null=True, verbose_name='Android Logs')),
                ('user', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='st_logs', to=settings.AUTH_USER_MODEL, verbose_name='profile')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
