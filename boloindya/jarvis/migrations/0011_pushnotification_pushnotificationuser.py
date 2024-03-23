# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-10-16 15:47
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('jarvis', '0010_fcmdevice_device_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='PushNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(blank=True, max_length=100, null=True, verbose_name='title')),
                ('description', models.CharField(blank=True, max_length=100, null=True, verbose_name='description')),
                ('language', models.CharField(blank=True, choices=[('0', 'All'), ('1', 'English'), ('2', 'Hindi'), ('3', 'Tamil'), ('4', 'Telgu')], default='0', max_length=10, null=True)),
                ('user_group', models.CharField(blank=True, choices=[('0', 'All')], default='0', max_length=10, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PushNotificationUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(blank=True, choices=[('0', 'Not Opened'), ('1', 'Opened')], default='0', max_length=10, null=True)),
                ('push_notification_id', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='push_notification_id', to='jarvis.PushNotification')),
                ('user', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='push_notification_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
