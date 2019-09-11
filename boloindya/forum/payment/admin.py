# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *
admin.site.register(PaymentCycle)
admin.site.register(EncashableDetail)
admin.site.register(PaymentInfo)

# Register your models here.
