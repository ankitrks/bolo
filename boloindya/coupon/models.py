# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from forum.core.conf import settings

# Create your models here.
class Coupon(models.Model):
    active_banner_img_url = models.TextField(blank = False, null = False)
    inactive_banner_img_url = models.TextField(blank=False, null=False)
    brand_name = models.TextField(blank = True, null = True)
    coins_required = models.PositiveIntegerField(default = 0)
    is_active = models.BooleanField(default=True)
    active_from = models.DateTimeField(auto_now=False, blank=False, null=False)
    active_till = models.DateTimeField(auto_now=False, blank=False, null=False)
    coupon_code = models.TextField(blank = False, null = False)
    discount_given = models.CharField(max_length=50, blank = True, null = True, default='')
    created_at=models.DateTimeField(auto_now=False,auto_now_add=True,blank=False,null=False)
    last_modified=models.DateTimeField(auto_now=True,auto_now_add=False)
    is_draft = models.BooleanField(default=False)

class UserCoupon(models.Model):
	coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, blank = False, null = False, related_name='coupons')
	created_at = models.DateTimeField(auto_now=False,auto_now_add=True,blank=False,null=False)
