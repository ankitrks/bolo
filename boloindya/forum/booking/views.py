# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import TemplateView


class BookingCallView(TemplateView):
    template_name = 'booking/index.html'

    def get(self, request, channel_id, *args, **kwargs):
        self.channel_id = channel_id
        return super(BookingCallView, self).get(request, channel_id, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BookingCallView, self).get_context_data(**kwargs)
        context.update({
            'app_id': "d09e29678db2414da0631caa9188a4f1",
            'channel_id': self.channel_id,
            'token': ''
        })
        return context
