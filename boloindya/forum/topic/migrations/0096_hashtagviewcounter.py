# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-05-06 05:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forum_topic', '0095_auto_20200427_1406'),
    ]

    operations = [
        migrations.CreateModel(
            name='HashtagViewCounter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(blank=True, choices=[(b'0', b'All'), (b'1', b'English'), (b'2', b'Hindi'), (b'3', b'Tamil'), (b'4', b'Telugu'), (b'5', b'Bengali'), (b'6', b'Kannada'), (b'7', b'Malayalam'), (b'8', b'Gujarati'), (b'9', b'Marathi'), (b'10', b'Punjabi'), (b'11', b'Odia')], max_length=10, null=True, verbose_name='language')),
                ('view_count', models.BigIntegerField(default=0)),
                ('video_count', models.PositiveIntegerField(default=0)),
                ('hashtag', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='hash_tag_counter', to='forum_topic.TongueTwister', verbose_name='HashTag')),
            ],
            options={
                'ordering': ['language'],
            },
        ),
    ]
