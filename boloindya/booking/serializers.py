from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Booking

class BookingSerializer(ModelSerializer):
	creator_id = SerializerMethodField()
	class Meta:
		model = Booking
		# fields = ('__all__')
		exclude = ('created_at', 'last_modified', 'creator')

	def get_creator_id(self, instance):
		return instance.creator_id