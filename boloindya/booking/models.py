# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField

from forum.topic.models import RecordTimeStamp
# Create your models here.
from datetime import date
import uuid

class Booking(RecordTimeStamp):
	creator = models.ForeignKey(settings.AUTH_USER_MODEL, blank = False, null = False, related_name='bookings')
	title = models.TextField(blank = False, null = False)
	description = models.TextField(blank = False, null = False)
	banner_img_url = models.TextField(blank = False, null = False)
	thumbnail_img_url = models.TextField(blank = False, null = False, default='')
	booking_count = models.PositiveIntegerField(default=0)
	like_count = models.PositiveIntegerField(default=0)
	is_active = models.BooleanField(default=False)

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

feature_options = (
	('0', "Allow Bookings For"),
)

class AppConfig(models.Model):
	"""
		This table is for to allow some user a specific fetaure just add that
		feature in feature_options
	"""
	feature_id = models.CharField(choices = feature_options,default="0", blank = True, null = True, max_length = 10)
	user_ids = ArrayField(models.CharField(max_length=200), blank=True)

	def __str__(self):
		return self.feature_id

class PayOutConfig(models.Model):
	commission_for_popular = models.CharField(max_length=10)
	commission_default = models.CharField(max_length=10)
	tnc_text = models.TextField(blank = True, null = True)

event_type_options = (
	("all","ALL"),
	("trending","Trending"),
	("recomended","Recomended")
	)
class Event(RecordTimeStamp):
	creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='events')
	title = models.TextField(blank = True, null = True)
	description = models.TextField(blank = True, null = True)
	banner_img_url = models.TextField(blank = True, null = True)
	thumbnail_img_url = models.TextField(blank = True, null = True)
	profile_pic_img_url = models.TextField(blank = True, null = True)
	event_count = models.PositiveIntegerField(default=0)
	like_count = models.PositiveIntegerField(default=0)
	price = models.PositiveIntegerField(default=0)
	hash_tags = models.ManyToManyField('forum_topic.TongueTwister',
			related_name="hash_tag_events",blank=True, null = True)
	category = models.ForeignKey('forum_category.Category', related_name="category_events",null=True,blank=True)
	language_ids = ArrayField(models.CharField(max_length=200), blank=True, default=list)
	is_approved = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	event_type = models.CharField(choices = event_type_options,default='all', blank = True, null = True, max_length = 25)

event_slot_options = (
	('available', "Available"),
	('booked', "Booked"),
	('hold',"Hold")
	)
class EventSlot(RecordTimeStamp):
	event = models.ForeignKey(Event, related_name='event_slot', on_delete=models.CASCADE)
	start_time = models.DateTimeField(auto_now=False, blank=False, null=False)
	end_time = models.DateTimeField(auto_now=False, blank=False, null=False)
	channel_id = models.TextField(null = True, blank=True, default=uuid.uuid4)
	state = models.CharField(choices = event_slot_options,default='available', blank = True, null = True, max_length = 25)

event_booking_state_options = (
	('draft', "Draft"),
	('booked', "Booked"),
	('cancelled', "Cancelled")
	)
event_booking_payment_options = (
	('draft', "Draft"),
	("initiated","Initiated"),
	('pending', "Pending"),
	('success', "Success"),
	('failed', "Failed")
	)
event_booking_payment_mode_options = (
	('card','Card'),
	)
class EventBooking(RecordTimeStamp):
	event = models.ForeignKey(Event, related_name='event_event_bookings', on_delete=models.CASCADE)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_event_bookings')
	event_slot = models.ForeignKey(EventSlot, related_name='event_slot_event_bookings')
	state = models.CharField(choices = event_booking_state_options,default='draft', max_length = 25)
	payment_status = models.CharField(choices = event_booking_payment_options,default='draft', max_length = 25)
	payment_gateway_order_id = models.TextField(blank = True, null = True)
	transaction_id = models.TextField(blank = True, null = True)
	payment_method = models.TextField(blank = True, null = True ,default="RazorPay")
	booking_number = models.TextField(blank = True, null = True)
	remark = models.TextField(blank = True, null = True)
	invoice_sent = models.BooleanField(default=False)
	payment_mode = models.CharField(choices = event_booking_payment_mode_options,default='card', max_length = 25)

	def save(self, *args, **kwargs):
		super(EventBooking, self).save(*args, **kwargs)
		if not self.booking_number:
			self.booking_number = 'BOOKING_' + str(self.pk)
			self.save()

class EventBookingInvoice(RecordTimeStamp):
	consumer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_event_booking_invoice')
	event_creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='creator_event_booking_invoice')
	price = models.DecimalField(max_digits = 10, decimal_places = 2,default=0.0)
	tax = models.DecimalField(max_digits = 10, decimal_places = 2,default=0.0)
	igst_percentage =  models.DecimalField(max_digits = 10, decimal_places = 2, default=18.0)
	net_amount_payble = models.DecimalField(max_digits = 10, decimal_places = 2,default=0.0)
	event_booking = models.ForeignKey(EventBooking, related_name='event_booking_invoice', on_delete=models.CASCADE)
	payment_mode = models.TextField(blank = True, null = True)
	discount = models.PositiveIntegerField(default=0)
	invoice_pdf_url = models.TextField(blank = True, null = True)
	invoice_number = models.TextField(blank = True, null = True)

	def save(self, *args, **kwargs):
		super(EventBookingInvoice, self).save(*args, **kwargs)
		if not self.invoice_number:
			today = date.today()
			current_month_invoice = EventBookingInvoice.objects.filter(created_at__year=today.year,created_at__month=today.month).count()
			next_invoice_counter = "%03d" % (current_month_invoice + 1,)
			self.invoice_number = str(today.strftime('%y'))+str(today.month)+str(next_invoice_counter)
			self.save()