from booking.models import Event, EventSlot
from datetime import datetime
import pandas as pd

class MarkOldEventInactive:
	def start(self):
		try:
			print("started")
			events = Event.objects.filter(is_approved=True,is_active=True).values('id')
			events_df = pd.DataFrame.from_records(events)
			if not events_df.empty:
				new_event_ids = list(set(list(EventSlot.objects.filter(event_id__in=events_df['id'].unique(), end_time__gt=datetime.now()).values_list('event_id',flat=True))))
				old_event_ids = [x for x in list(events_df['id'].unique()) if x not in new_event_ids]
				Event.objects.filter(id__in=old_event_ids).update(is_active = False)
			print("done")
		except Exception as e:
			print("exception "+str(e))

def run():
	MarkOldEventInactive().start()