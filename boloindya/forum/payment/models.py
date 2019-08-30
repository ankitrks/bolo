# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _
from forum.topic.models import RecordTimeStamp, UserInfo

class PaymentCycle(models.Model):
	duration_type_options = (
    ('1', "Day"),
    ('2', "Week"),
    ('3', "Month"),
    ('4', "Year"),
    )
	duration_type = models.CharField(_("Duration Type"), choices=duration_type_options,max_length=10,null=True,blank=True)
	duration_period = models.PositiveIntegerField(_("Duration Period"),null=True,blank=True)
	duration_start_date = models.DateField(_("Duration Start Date"),null=True,blank=True)
	minimum_bolo_score = models.PositiveIntegerField(_("Minimum Bolo Score For Eligibility"),null=True,blank=True,default=0)

	def __unicode__(self):
        return self.minimum_bolo_score

    class Meta:
        verbose_name = _("PaymentCycle")
        verbose_name_plural = _("PaymentCycle's")

class EncashableDetail(UserInfo):
	duration_start_date = models.DateField(_("Duration Start Date"),null=True,blank=True)
	duration_end_date = models.DateField(_("Duration End Date"),null=True,blank=True)
	bolo_score_earned = models.PositiveIntegerField(_("Bolo Scores Earned"),null=True,blank=True,default=0)
	is_encashed = models.BooleanField(_("Is Encashed?"),null=True,blank=True,default=False)
	enchashed_on = models.DateTimeField(null=True,blank=True)
	is_eligible_for_encash = models.BooleanField(_("Is Eligible For Encash?"),null=True,blank=True,default=False)

	def __unicode__(self):
        return self.user.username

    class Meta:
        verbose_name = _("EncashableDetail")
        verbose_name_plural = _("EncashableDetail's")


class PaymentInfo(UserInfo):
	transaction_choices_options = (
		('1','Bank Account'),
		('2','Paytm'),
		)
	encashble_detail = models.ForeignKey(EncashableDetail,null=True,blank=True)
	amount = models.PositiveIntegerField(null=True,blank=True,default=0)
	transaction_method = models.CharField(_('Transaction Method'),choices=transaction_choices_options,null=True,blank=True,default='2',max_length=10)
	transaction_number = models.CharField(_('Transaction Number'),max_length=255,null=True,blank=True)

	def __unicode(self):
		return self.user.username

	class Meta:
		verbose_name = _("PaymentInfo")
        verbose_name_plural = _("PaymentInfo's")
