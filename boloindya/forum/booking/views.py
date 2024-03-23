# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.views.generic import TemplateView
from django.conf import settings
from booking.models import BookingSlot, EventSlot
from datetime import datetime, timedelta
from sentry_sdk import capture_exception
import jwt

class BookingCallView(TemplateView):
    template_name = 'booking/index.html'
    failed_template_name = 'payment/payin/booking_403.html'

    def get(self, request, channel_id, *args, **kwargs):
        self.channel_id = channel_id
        self.is_allowed = True #False
        try:
            is_authenticated, current_logged_in_user = self.get_user_from_token()
            if is_authenticated:
                allowed_user_ids = []
                event_slot = EventSlot.objects.select_related('event').get(channel_id=channel_id)
                allowed_user_ids.append(event_slot.event.creator_id)
                allowed_user_ids+= list(event_slot.event_slot_event_bookings.filter(payment_status='success').values_list('user_id',flat=True))
                if int(current_logged_in_user) in allowed_user_ids:
                    self.is_allowed = True
        except Exception as e:
            print(e)
            capture_exception(e)
        return super(BookingCallView, self).get(request, channel_id, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BookingCallView, self).get_context_data(**kwargs)
        is_active = False
        try:
            current_time = datetime.now()
            booking_slot = BookingSlot.objects.get(channel_id=self.channel_id)
            if booking_slot.start_time<=current_time<=booking_slot.end_time:
                is_active = True
        except:
            pass
        context.update({
            'app_id': "d09e29678db2414da0631caa9188a4f1",
            'channel_id': self.channel_id,
            'token': '',
            'is_active': is_active
        })
        return context

    def get_template_names(self):
        if self.is_allowed:
            return [self.template_name]
        else:
            return [self.failed_template_name]

    def get_user_from_token(self):
        if 'HTTP_AUTHORIZATION' in self.request.META:
            token = self.request.META['HTTP_AUTHORIZATION'].split()[-1]
            user_data = jwt.decode(token, settings.SECRET_KEY)
            return True, user_data['user_id']
        else:
            return False, ''