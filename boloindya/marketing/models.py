# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

class AdStats(models.Model):
    ad = models.ForeignKey('advertisement.Ad', related_name='stats')
    date = models.DateField(_("Date"))
    view_count = models.PositiveIntegerField(_('Views'), default=0)
    install_count = models.PositiveIntegerField(_('Install'), default=0)
    skip_count = models.PositiveIntegerField(_('Skips'), default=0)
    full_watched = models.PositiveIntegerField(_('Full ad watched'), default=0)
    skip_playtime = models.PositiveIntegerField(_('Playtime'), default=0)
    install_playtime = models.PositiveIntegerField(_('Playtime'), default=0)


class EventStats(models.Model):
    event = models.ForeignKey('booking.Event', related_name='stats')
    date = models.DateField(_('Date'))
    view_count = models.PositiveIntegerField(_('Views'), default=0)
    click_count = models.PositiveIntegerField(_('Click'), default=0)
    payment_initiated_count = models.PositiveIntegerField(_('Payment Initiated'), default=0)
    confirm_booking_count = models.PositiveIntegerField(_('Confirm Booking'), default=0)
    total_revenue = models.PositiveIntegerField(_('Total Revenue'), default=0)
