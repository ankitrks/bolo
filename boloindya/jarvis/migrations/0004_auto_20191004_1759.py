# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-10-04 17:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jarvis', '0003_auto_20191003_1320'),
    ]

    operations = [
        migrations.AddField(
            model_name='videocategory',
            name='slug',
            field=models.SlugField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='videouploadtranscode',
            name='is_free_video',
            field=models.BooleanField(default=False, verbose_name='Is Free Video?'),
        ),
        migrations.AddField(
            model_name='videouploadtranscode',
            name='video_descp',
            field=models.TextField(blank=True, null=True, verbose_name='Video Description'),
        ),
        migrations.AddField(
            model_name='videouploadtranscode',
            name='video_title',
            field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='Video Title'),
        ),
    ]
