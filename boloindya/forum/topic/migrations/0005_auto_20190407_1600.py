# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-07 16:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forum_topic', '0004_topic_language_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='category_topics', to='forum_category.Category', verbose_name='category'),
        ),
    ]
