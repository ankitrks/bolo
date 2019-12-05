# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-12-05 15:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum_topic', '0071_auto_20191202_1927'),
    ]

    operations = [
        migrations.AddField(
            model_name='tonguetwister',
            name='hash_counter',
            field=models.PositiveIntegerField(blank=True, default=1, null=True),
        ),
        migrations.AddField(
            model_name='topic',
            name='hash_tags',
            field=models.ManyToManyField(blank=True, related_name='hash_tag_topics', to='forum_topic.TongueTwister', verbose_name='hash_tags'),
        ),
    ]
