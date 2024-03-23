# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class PaymentConfig(AppConfig):
    name = 'forum.payment'
    verbose_name = "Forum User Payment"
    label = 'forum_payment'
    