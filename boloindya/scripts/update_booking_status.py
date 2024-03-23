from booking.models import UserBooking, BookingSlot
from datetime import datetime, timedelta

def run():
	current_time = datetime.now()
	expired_slots = list(BookingSlot.objects.filter(end_time__lt=datetime.now()).values_list('id', flat=True))
	print(expired_slots)
	if expired_slots:
		UserBooking.objects.filter(booking_slot_id__in=expired_slots).update(booking_status=2)

	active_slots = list(BookingSlot.objects.filter(start_time__lte=datetime.now(),end_time__gte=datetime.now()).values_list('id', flat=True))
	if active_slots:
		UserBooking.objects.filter(booking_slot_id__in=active_slots).update(booking_status=1)