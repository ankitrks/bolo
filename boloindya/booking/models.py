# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings

from forum.topic.models import RecordTimeStamp
# Create your models here.
import uuid


class Booking(RecordTimeStamp):
	creator = models.ForeignKey(settings.AUTH_USER_MODEL, blank = False, null = False, related_name='bookings')
	title = models.TextField(blank = False, null = False)
	description = models.TextField(blank = False, null = False)
	banner_img_url = models.TextField(blank = False, null = False)
	thumbnail_img_url = models.TextField(blank = False, null = False, default='')
	booking_count = models.PositiveIntegerField(default=0)
	like_count = models.PositiveIntegerField(default=0)

booking_options = (
	('0', "Booked"),
	('1', "Session Started"),
	('2', "Session Ended")
)
class BookingSlot(RecordTimeStamp):
	booking = models.ForeignKey(Booking, blank = False, null = False, related_name='booking_slot', on_delete=models.CASCADE)
	start_time = models.DateTimeField(auto_now=False, blank=False, null=False)
	end_time = models.DateTimeField(auto_now=False, blank=False, null=False)
	channel_id = models.TextField(null = False, blank=False, default=uuid.uuid4)

class UserBooking(RecordTimeStamp):
	booking = models.ForeignKey(Booking, blank = False, null = False, related_name='user_booking', on_delete=models.CASCADE)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, blank = False, null = False, related_name='user_bookings')
	booking_slot = models.ForeignKey(BookingSlot, blank = False, null = False, related_name='booking_slot_user')
	booking_status = models.CharField(choices = booking_options,default=0, blank = True, null = True, max_length = 10)

	class Meta:
		unique_together = ('user', 'booking_slot',)