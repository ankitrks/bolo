# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-07-16 14:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_category', '0012_auto_20190503_1444'),
        ('forum_topic', '0043_topic_likes_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='m2mcategory',
            field=models.ManyToManyField(blank=True, null=True, related_name='m2mcategories_topics', to='forum_category.Category', verbose_name='m2mcategories'),
        ),
    ]
