# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings

from forum.topic.models import RecordTimeStamp
# Create your models here.


class Booking(RecordTimeStamp):
	creator = models.ForeignKey(settings.AUTH_USER_MODEL, blank = False, null = False, related_name='bookings')
	title = models.TextField(blank = False, null = False)
	description = models.TextField(blank = False, null = False)
	banner_img_url = models.TextField(blank = False, null = False)
	thumbnail_img_url = models.TextField(blank = False, null = False, default='')
	booking_count = models.PositiveIntegerField(default=0)
	like_count = models.PositiveIntegerField(default=0)
	available_slots = models.PositiveIntegerField(default=0)
	# inactive_banner_img_url = models.TextField(blank=False, null=False)
	# brand_name = models.TextField(blank = True, null = True)
	# coins_required = models.PositiveIntegerField(default = 0)
	# is_active = models.BooleanField(default=True)
	# active_from = models.DateTimeField(auto_now=False, blank=False, null=False)
	# active_till = models.DateTimeField(auto_now=False, blank=False, null=False)
	# coupon_code = models.TextField(blank = False, null = False)
	# discount_given = models.CharField(max_length=50, blank = True, null = True, default='')
	# created_at=models.DateTimeField(auto_now=False,auto_now_add=True,blank=False,null=False)
	# last_modified=models.DateTimeField(auto_now=True,auto_now_add=False)
	# is_draft = models.BooleanField(default=False)

booking_options = (
	('0', "Booked"),
	('1', "Session Started"),
	('2', "Session Ended")
)
class BookingSlot(RecordTimeStamp):
	booking = models.ForeignKey(Booking, blank = False, null = False, related_name='booking_slot', on_delete=models.CASCADE)
	start_time = models.DateTimeField(auto_now=False, blank=False, null=False)
	end_time = models.DateTimeField(auto_now=False, blank=False, null=False)

class UserBooking(RecordTimeStamp):
	booking = models.ForeignKey(Booking, blank = False, null = False, related_name='user_booking', on_delete=models.CASCADE)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, blank = False, null = False, related_name='user_bookings')
	booking_slot = models.ForeignKey(BookingSlot, blank = False, null = False, related_name='booking_slot_user')
	booking_status = models.CharField(choices = booking_options,default=0, blank = True, null = True, max_length = 10)