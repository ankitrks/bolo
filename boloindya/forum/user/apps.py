# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.apps import AppConfig


class SpiritUserConfig(AppConfig):

    name = 'forum.user'
    verbose_name = "Forum User"
    label = 'forum_user'

    def ready(self):
        self.register_signals()

    def register_signals(self):
        from . import signals
