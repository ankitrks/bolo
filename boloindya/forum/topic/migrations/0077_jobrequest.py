# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-01-07 16:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forum_topic', '0076_auto_20200107_1503'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('name', models.TextField(blank=True, null=True, verbose_name='Username')),
                ('email', models.TextField(blank=True, null=True, verbose_name='Email')),
                ('mobile', models.TextField(blank=True, null=True, verbose_name='Mobile')),
                ('user_doc', models.TextField(blank=True, null=True, verbose_name='document')),
                ('jobOpening', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_opening', to='forum_topic.JobOpening')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
