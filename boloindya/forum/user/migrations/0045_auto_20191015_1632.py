# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-10-15 16:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_user', '0044_videoplaytime'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoCompleteRate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(db_index=True, max_length=250, null=True, verbose_name='user')),
                ('videoid', models.CharField(db_index=True, max_length=250, null=True, verbose_name='videoid')),
                ('duration', models.PositiveIntegerField(default=0, editable=False, verbose_name='duration')),
                ('playtime', models.PositiveIntegerField(default=0, editable=False, verbose_name='playtime')),
                ('percentage_viewed', models.PositiveIntegerField(default=0, editable=False, verbose_name='percentage_viewed')),
            ],
        ),
        migrations.RemoveField(
            model_name='videoplaytime',
            name='duration',
        ),
        migrations.AddField(
            model_name='videoplaytime',
            name='playtime',
            field=models.PositiveIntegerField(default=0, editable=False, verbose_name='playtime'),
        ),
    ]
