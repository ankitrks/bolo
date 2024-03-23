# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-07 14:06
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum_topic', '0030_notification'),
    ]

    operations = [
        migrations.CreateModel(
            name='FCMDevice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dev_id', models.CharField(max_length=50, unique=True, verbose_name=b'Device ID')),
                ('reg_id', models.CharField(max_length=255, unique=True, verbose_name=b'Registration ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name=b'Name')),
                ('is_active', models.BooleanField(default=False, verbose_name=b'Is active?')),
                ('user', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='forum_topic_fcmdevice_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Device',
                'verbose_name_plural': 'Devices',
            },
        ),
        migrations.RemoveField(
            model_name='notification',
            name='device_id',
        ),
    ]
