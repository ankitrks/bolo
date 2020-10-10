# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import TemplateView

from booking.models import BookingSlot

from datetime import datetime, timedelta

class BookingCallView(TemplateView):
    template_name = 'booking/index.html'

    def get(self, request, channel_id, *args, **kwargs):
        self.channel_id = channel_id
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
