# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-07-09 13:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_topic', '0108_auto_20200708_2354'),
    ]

    operations = [
        migrations.AddField(
            model_name='tonguetwister',
            name='si_descpription',
            field=models.TextField(blank=True, null=True, verbose_name='Sinhala Hash Tag Description'),
        ),
        migrations.AlterField(
            model_name='hashtagviewcounter',
            name='language',
            field=models.CharField(blank=True, choices=[(b'0', b'All'), (b'1', b'English'), (b'2', b'Hindi'), (b'3', b'Tamil'), (b'4', b'Telugu'), (b'5', b'Bengali'), (b'6', b'Kannada'), (b'7', b'Malayalam'), (b'8', b'Gujarati'), (b'9', b'Marathi'), (b'10', b'Punjabi'), (b'11', b'Odia'), (b'12', b'Bhojpuri'), (b'13', b'Haryanvi'), (b'14', b'Sinhala')], max_length=10, null=True, verbose_name='language'),
        ),
        migrations.AlterField(
            model_name='tonguetwistercounter',
            name='language_id',
            field=models.CharField(blank=True, choices=[(b'0', b'All'), (b'1', b'English'), (b'2', b'Hindi'), (b'3', b'Tamil'), (b'4', b'Telugu'), (b'5', b'Bengali'), (b'6', b'Kannada'), (b'7', b'Malayalam'), (b'8', b'Gujarati'), (b'9', b'Marathi'), (b'10', b'Punjabi'), (b'11', b'Odia'), (b'12', b'Bhojpuri'), (b'13', b'Haryanvi'), (b'14', b'Sinhala')], db_index=True, default='1', max_length=10, null=True, verbose_name='language'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='language_id',
            field=models.CharField(blank=True, choices=[(b'0', b'All'), (b'1', b'English'), (b'2', b'Hindi'), (b'3', b'Tamil'), (b'4', b'Telugu'), (b'5', b'Bengali'), (b'6', b'Kannada'), (b'7', b'Malayalam'), (b'8', b'Gujarati'), (b'9', b'Marathi'), (b'10', b'Punjabi'), (b'11', b'Odia'), (b'12', b'Bhojpuri'), (b'13', b'Haryanvi'), (b'14', b'Sinhala')], db_index=True, default='1', max_length=10, null=True, verbose_name='language'),
        ),
    ]
