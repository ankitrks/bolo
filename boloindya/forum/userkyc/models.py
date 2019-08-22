# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _
from forum.topic.models import RecordTimeStamp, UserInfo

class UserKYC(UserInfo):
    kyc_basic_info_submitted = models.BooleanField(default = False)
    is_kyc_basic_info_accepted = models.BooleanField(default = False)
    kyc_document_info_submitted = models.BooleanField(default = False)
    is_kyc_document_info_accepted = models.BooleanField(default = False)
    kyc_pan_info_submitted = models.BooleanField(default = False)
    is_kyc_pan_info_accepted = models.BooleanField(default = False)
    kyc_selfie_info_submitted = models.BooleanField(default = False)
    is_kyc_selfie_info_accepted = models.BooleanField(default = False)
    kyc_additional_info_submitted = models.BooleanField(default = False)
    is_kyc_additional_info_accepted = models.BooleanField(default = False)
    is_kyc_completed = models.BooleanField(default = False)
    is_kyc_accepted = models.BooleanField(default = False)
    # last_step_performed = model.CharField(to get know the last step of user )

    def __unicode__(self):
        return self.user.username

    class Meta:
        ordering = ['-is_kyc_accepted']
        verbose_name = _("UserKyc")
        verbose_name_plural = _("UserKYC's")

class KYCBasicInfo(UserInfo):
    first_name = models.CharField(_("First Name"), max_length=255, blank=True)
    middle_name = models.CharField(_("Middle Name"), max_length=255, blank=True)
    lastname_name = models.CharField(_("Last Name"), max_length=255, blank=True)
    d_o_b = models.DateField(auto_now_add = False, auto_now = False, blank = True, null = True)
    mobile_no = models.CharField(_("Mobile No"), max_length=100, blank = True, null = True)
    is_mobile_verified = models.BooleanField(default = False)
    email = models.EmailField(blank = True, null = True)
    is_email_verified = models.BooleanField(default = False)
    pic_selfie_url = models.CharField(_("Pic Selfie"), max_length=1000, blank=True)
    # nationality = models.CharField(choice field for selecting country)

    def __unicode__(self):
        return self.user.username

    class Meta:
        verbose_name = _("KYCbasicInfo")
        verbose_name_plural = _("KYCbasicInfo's")

class KYCDocumentType(RecordTimeStamp):
    document_name = models.CharField(_("Document Name"), max_length=255, blank=True)
    no_image_required = models.PositiveIntegerField(null=True,blank=True,default=1)

    def __unicode__(self):
        return self.document_name

    class Meta:
        verbose_name = _("KYCDocumentType")
        verbose_name_plural = _("KYCDocumentType's")

class KYCDocument(UserInfo):
    kyc_document_type = models.ForeignKey(KYCDocumentType, related_name='documents',null=True,blank=True)
    frontside_url = models.CharField(_("Document Front Url"), max_length=1000, blank=True)
    backside_url= models.CharField(_("Document Back Url"), max_length=1000, blank=True)

    def __unicode__(self):
        return self.user.username

    class Meta:
        verbose_name = _("KYCDocument")
        verbose_name_plural = _("KYCDocument's")

class AdditionalInfo(UserInfo):
    profession_options = (
    ('1', "Govermnet Employee"),
    ('2', "Private Sector"),
    ('3', "Business"),
    ('99', "Others"),
    )
    status_options = (
        ('1', "Single"),
        ('2', "Married"),
        ('3', "Divorced"),
        )
    father_firstname = models.CharField(_("Father First Name"), max_length=255, blank=True)
    father_lastname = models.CharField(_("Father Last Name"), max_length=255, blank=True)
    mother_firstname = models.CharField(_("Mother First Name"), max_length=255, blank=True)
    mother_lastname = models.CharField(_("Mother Last Name"), max_length=255, blank=True)
    profession = models.CharField(choices=profession_options, blank = True, null = True, max_length=10, default='99')
    status = models.CharField(choices=status_options, blank = True, null = True, max_length=10, default='1')

    def __unicode__(self):
        return self.user.username

    class Meta:
        verbose_name = _("AdditionalInfo")
        verbose_name_plural = _("AdditionalInfo's")

class BankDetail(UserInfo):
    bank_name = models.CharField(_("Bank Name"), max_length=255, blank=True)# later it will be replaced with the choice field
    account_number = models.CharField(_("Account Number"), max_length=255, blank=True)
    IFSC_code = models.CharField(_("IFSC Code"), max_length=255, blank=True)# prevalidate in backend and allow to seacrh in frontedn

    def __unicode__(self):
        return self.user.username

    class Meta:
        verbose_name = _("BankDetail")
        verbose_name_plural = _("BankDetail's")





