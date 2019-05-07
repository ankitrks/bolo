# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.apps import AppConfig


class SpiritTopicConfig(AppConfig):
    name = 'forum.topic'
    verbose_name = "Forum Topic"
    label = 'forum_topic'
    def ready(self):
        import forum.topic.signals  # noqa
