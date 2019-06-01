# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-29 15:19
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum_topic', '0035_notification_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255, null=True, verbose_name='Title')),
                ('image', models.CharField(blank=True, max_length=255, null=True, verbose_name='Option Image')),
                ('is_correct_choice', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='CricketMatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('match_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Match Name')),
                ('team_1', models.CharField(blank=True, max_length=255, null=True, verbose_name='Team 1')),
                ('team_1_flag', models.TextField(blank=True, null=True, verbose_name='Team 1 Flag')),
                ('team_2', models.CharField(blank=True, max_length=255, null=True, verbose_name='Team 2')),
                ('team_2_flag', models.TextField(blank=True, null=True, verbose_name='Team 2 Flag')),
                ('match_datetime', models.DateTimeField(blank=True, null=True, verbose_name='Match Datetime')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Leaderboard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('total_score', models.PositiveIntegerField(default=0, verbose_name='Total Score')),
                ('total_prediction_count', models.PositiveIntegerField(default=0, verbose_name='Total Prediction')),
                ('correct_prediction_count', models.PositiveIntegerField(default=0, verbose_name='Correct Prediction')),
                ('user', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='forum_topic_leaderboard_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255, null=True, verbose_name='Title')),
                ('activate_datetime', models.DateTimeField(blank=True, null=True, verbose_name='Activate DateTime')),
                ('deactivate_datetime', models.DateTimeField(blank=True, null=True, verbose_name='Deactivate DateTime')),
                ('score', models.PositiveIntegerField(default=0, verbose_name='Score')),
                ('bolo_score', models.PositiveIntegerField(default=0, verbose_name='Bolo Score')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('cricketmatch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='st_cricket_match', to='forum_topic.CricketMatch')),
            ],
        ),
        migrations.CreateModel(
            name='Voting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('choice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='st_voting_choice', to='forum_topic.Choice')),
                ('cricketmatch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='st_voting_poll', to='forum_topic.CricketMatch')),
                ('poll', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='st_voting_match', to='forum_topic.Poll')),
                ('user', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='forum_topic_voting_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='choice',
            name='poll',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='st_cricket_match_choice', to='forum_topic.Poll'),
        ),
    ]
