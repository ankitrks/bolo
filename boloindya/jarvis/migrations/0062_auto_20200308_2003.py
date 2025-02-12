# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-03-08 20:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jarvis', '0061_remove_dashboardmetricsjarvis_category_slab_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dashboardmetricsjarvis',
            name='metrics_language_options',
            field=models.CharField(blank=True, choices=[(b'0', b'All'), (b'1', b'English'), (b'2', b'Hindi'), (b'3', b'Tamil'), (b'4', b'Telugu'), (b'5', b'Bengali'), (b'6', b'Kannada'), (b'7', b'Malayalam'), (b'8', b'Gujarati'), (b'9', b'Marathi'), (b'10', b'Punjabi'), (b'11', b'Odia')], default='0', max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='pushnotification',
            name='language',
            field=models.CharField(blank=True, choices=[(b'0', b'All'), (b'1', b'English'), (b'2', b'Hindi'), (b'3', b'Tamil'), (b'4', b'Telugu'), (b'5', b'Bengali'), (b'6', b'Kannada'), (b'7', b'Malayalam'), (b'8', b'Gujarati'), (b'9', b'Marathi'), (b'10', b'Punjabi'), (b'11', b'Odia')], default='0', max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='statedistrictlanguage',
            name='district_language',
            field=models.CharField(blank=True, choices=[(b'0', b'All'), (b'1', b'English'), (b'2', b'Hindi'), (b'3', b'Tamil'), (b'4', b'Telugu'), (b'5', b'Bengali'), (b'6', b'Kannada'), (b'7', b'Malayalam'), (b'8', b'Gujarati'), (b'9', b'Marathi'), (b'10', b'Punjabi'), (b'11', b'Odia')], default='1', max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='statedistrictlanguage',
            name='state_language',
            field=models.CharField(blank=True, choices=[(b'0', b'All'), (b'1', b'English'), (b'2', b'Hindi'), (b'3', b'Tamil'), (b'4', b'Telugu'), (b'5', b'Bengali'), (b'6', b'Kannada'), (b'7', b'Malayalam'), (b'8', b'Gujarati'), (b'9', b'Marathi'), (b'10', b'Punjabi'), (b'11', b'Odia')], default='1', max_length=10, null=True),
        ),
    ]
