from booking.models import *
from django.core import serializers
import pandas as pd
import json

def run():
	booking_ids = list(Booking.objects.all().values_list('id',flat=True))
	for booking_id in booking_ids:
		print("starting for booking id "+str(booking_id))
		booking_json  = Booking.objects.filter(id=booking_id).values("creator_id","title","description","banner_img_url","thumbnail_img_url","like_count")[0]
		booking_json['is_approved'] = True
		event = Event(**booking_json)
		event.save()
		booking_slots = BookingSlot.objects.filter(booking_id=booking_id).values('id','start_time','end_time','channel_id')
		for booking_slot in booking_slots:
			booking_slot_id = booking_slot.pop("id",None)
			booking_slot['event_id'] = event.id
			booking_slot['state'] = 'booked'
			event_slot = EventSlot(**booking_slot)
			event_slot.save()
			user_booking = UserBooking.objects.filter(booking_id=booking_id, booking_slot_id=booking_slot_id).values('user_id')
			if user_booking:
				user_booking_json = user_booking[0]
				user_booking_json['event_id'] = event.id
				user_booking_json['event_slot_id'] = event_slot.id
				user_booking_json['state'] = 'booked'
				user_booking_json['payment_status'] = 'success'
				EventBooking(**user_booking_json).save()
	print("done")