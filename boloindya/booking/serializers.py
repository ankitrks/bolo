from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Booking, PayOutConfig, Event, EventBooking

class BookingSerializer(ModelSerializer):
	creator_id = SerializerMethodField()
	creator_name = SerializerMethodField()
	class Meta:
		model = Booking
		# fields = ('__all__')
		exclude = ('created_at', 'last_modified', 'creator')

	def get_creator_id(self, instance):
		return instance.creator_id

	def get_creator_name(self, instance):
		user = instance.creator
		return (user.first_name+user.last_name) or (user.username)

class PayOutConfigSerializer(ModelSerializer):
	class Meta:
		model = PayOutConfig
		fields = ('__all__')

class EventSerializer(ModelSerializer):
	class Meta:
		model = Event
		fields = ('__all__')

class EventBookingSerializer(ModelSerializer):
	creator_username = SerializerMethodField()
	event_title = SerializerMethodField()
	event_description = SerializerMethodField()
	event_slot_start_time = SerializerMethodField()
	event_slot_end_time = SerializerMethodField()
	price = SerializerMethodField()
	booked_by_username = SerializerMethodField()
	class Meta:
		model = EventBooking
		fields = ('__all__')

	def get_creator_username(self, instance):
		return instance.event.creator.username
	def get_event_title(self, instance):
		return instance.event.title
	def get_event_description(self, instance):
		return instance.event.description
	def get_event_slot_start_time(self, instance):
		return instance.event_slot.start_time
	def get_event_slot_end_time(self, instance):
		return instance.event_slot.end_time
	def get_price(self, instance):
		return instance.event.price
	def get_booked_by_username(self, instance):
		return instance.user.username