# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(UserKYC)
admin.site.register(KYCBasicInfo)
admin.site.register(KYCDocumentType)
admin.site.register(KYCDocument)
admin.site.register(AdditionalInfo)
admin.site.register(BankDetail)
