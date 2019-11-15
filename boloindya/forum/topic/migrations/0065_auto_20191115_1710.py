# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-11-15 17:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_topic', '0064_auto_20191111_1630'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='audio_m3u8_content',
            field=models.TextField(blank=True, null=True, verbose_name='Audio M3U8 Content'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='m3u8_content',
            field=models.TextField(blank=True, null=True, verbose_name='M3U8 Content'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='video_m3u8_content',
            field=models.TextField(blank=True, null=True, verbose_name='Video M3U8 Content'),
        ),
    ]
