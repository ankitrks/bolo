# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-03-08 20:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_topic', '0089_topic_old_backup_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='tonguetwister',
            name='od_descpription',
            field=models.TextField(blank=True, null=True, verbose_name='Odia Hash Tag Description'),
        ),
        migrations.AddField(
            model_name='tonguetwister',
            name='pb_descpription',
            field=models.TextField(blank=True, null=True, verbose_name='Punjabi Hash Tag Description'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='language_id',
            field=models.CharField(blank=True, choices=[(b'0', b'All'), (b'1', b'English'), (b'2', b'Hindi'), (b'3', b'Tamil'), (b'4', b'Telugu'), (b'5', b'Bengali'), (b'6', b'Kannada'), (b'7', b'Malayalam'), (b'8', b'Gujarati'), (b'9', b'Marathi'), (b'10', b'Punjabi'), (b'11', b'Odia')], db_index=True, default='1', max_length=10, null=True, verbose_name='language'),
        ),
    ]
