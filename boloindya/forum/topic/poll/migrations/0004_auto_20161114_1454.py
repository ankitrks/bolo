# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-14 14:54
from __future__ import unicode_literals

from django.db import migrations


def clean_content_type(apps, schema_editor):
    content_types = apps.get_model('contenttypes.ContentType')
    content_types.objects.filter(
        app_label='forum_topic_poll',
        model__in=[
            'TopicPoll'.lower(),
            'TopicPollChoice'.lower(),
            'TopicPollVote'.lower()]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('forum_topic_poll', '0003_auto_20161114_1452'),
    ]

    operations = [
        migrations.RunPython(clean_content_type),
    ]
