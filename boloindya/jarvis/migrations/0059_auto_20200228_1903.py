# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-02-28 19:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forum_category', '0019_auto_20200205_1542'),
        ('jarvis', '0058_auto_20200228_1711'),
    ]

    operations = [
        migrations.AddField(
            model_name='dashboardmetricsjarvis',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='jarvis_dashboardmetricsjarvis_category', to='forum_category.Category', verbose_name='category'),
        ),
        
    ]
