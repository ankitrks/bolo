# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-06-19 00:18
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum_topic', '0040_topic_last_commented'),
    ]

    operations = [
        migrations.CreateModel(
            name='VBseen',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='topic',
            name='is_vb',
            field=models.BooleanField(default=False, verbose_name='Is Video Bytes'),
        ),
        migrations.AddField(
            model_name='vbseen',
            name='topic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vb_seen', to='forum_topic.Topic'),
        ),
        migrations.AddField(
            model_name='vbseen',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='forum_topic_vbseen_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
