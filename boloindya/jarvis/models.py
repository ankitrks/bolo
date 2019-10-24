# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.template.defaultfilters import slugify
from fcm.models import AbstractDevice
from django.http import JsonResponse

from django.db.models import Q

from forum.topic.models import RecordTimeStamp

class VideoCategory(models.Model):
    category_name = models.CharField(_('Category Name'),max_length=100,null=True,blank=True)
    slug = models.SlugField(max_length=100)

    def __unicode__(self):
        return self.category_name

    def save(self, *args, **kwargs):
        self.slug= slugify(self.category_name)
        super(VideoCategory, self).save(*args, **kwargs)

class VideoUploadTranscode(models.Model):
    s3_file_url = models.CharField(_("S3 File URL"),null=True,blank=True,max_length=1000)
    category = models.ForeignKey(VideoCategory,null=True,blank=True)
    transcoded_file_url = models.CharField(_("Transcoded File URL"),null=True,blank=True,max_length=1000)
    transcode_job_id = models.TextField(_("Transcode Job ID"), blank = True)
    transcode_dump = models.TextField(_("Transcode Dump"), blank = True)
    filename_uploaded = models.CharField(_("Filename Uploaded"),null=True,blank=True,max_length=1000)
    filename_changed = models.CharField(_("Filename changed"),null=True,blank=True,max_length=1000)
    folder_to_upload = models.CharField(_("Filename changed"),null=True,blank=True,max_length=1000)
    folder_to_upload_changed = models.CharField(_("Filename changed"),null=True,blank=True,max_length=1000)
    is_free_video = models.BooleanField(_("Is Free Video?"),default=False)
    video_title = models.CharField(_("Video Title"),null=True,blank=True,max_length=1000)
    slug = models.SlugField(max_length=1000)
    video_descp = models.TextField(_("Video Description"),null=True,blank=True)
    meta_title = models.CharField(_("Meta Title"),null=True,blank=True,max_length=1000)
    meta_descp = models.TextField(_("Meta Description"),null=True,blank=True)
    meta_keywords = models.CharField(_("Meta Keywords"),null=True,blank=True,max_length=1000)
    thumbnail_url = models.CharField(_("Thumbnail URL"),null=True,blank=True,max_length=1000)
    media_duration = models.CharField(_("duration"), max_length=20, default='',null=True,blank=True)
    is_active = models.BooleanField(default=True)
    
    def __unicode__(self):
        return self.filename_uploaded

    def save(self, *args, **kwargs):
        if self.video_title:
            self.slug= slugify(self.video_title)
        super(VideoUploadTranscode, self).save(*args, **kwargs)

device_options = (
    ('1', "Android"),
    ('2', "iOS"),
    ('3', "Web"),
)

class FCMDevice(AbstractDevice):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, related_name='%(app_label)s_%(class)s_user',editable=False)
    device_type = models.CharField(choices=device_options, blank = True, null = True, max_length=10, default='0')
    created_at=models.DateTimeField(auto_now=False,auto_now_add=True,blank=False,null=False) # auto_now will add the current time and date whenever field is saved.
    last_modified=models.DateTimeField(auto_now=True,auto_now_add=False)                     # while auto_now_add will save the date and time only when record is first created

    def __unicode__(self):
        return str(self.user)


    def register_device(self,request):
        reg_id = request.POST.get('reg_id')
        dev_id=request.POST.get('dev_id')
        try:
            instance = FCMDevice.objects.filter(Q(reg_id = reg_id) | Q(dev_id = dev_id))
            if not len(instance):
                print 'Not Exists'
                raise Exception
            print 'Exisits'
            if request.user.id == None:
                print 'AnonymousUser'
                instance.update(is_active = True,dev_id=dev_id,device_type = request.POST.get('device_type'), reg_id=reg_id) 
            else:
                print 'User'
                instance.update(user = request.user,is_active = True,name=request.user.username,dev_id=dev_id,device_type = request.POST.get('device_type'),reg_id=reg_id)
            return JsonResponse({"status":"Success"},safe = False)
        except Exception as e:
            if request.user.id == None:
                print 'AnonymousUser'
                instance = FCMDevice.objects.create(reg_id = request.POST.get('reg_id'),name='Anonymous',dev_id=request.POST.get('dev_id'),device_type = request.POST.get('device_type'))
            else:
                instance = FCMDevice.objects.create(user = request.user,reg_id = request.POST.get('reg_id'),name=request.user.username,dev_id=request.POST.get('dev_id'),device_type = request.POST.get('device_type'))
            return JsonResponse({"status":"Success"},safe = False)
        # try:
        #     instance = FCMDevice.objects.filter(reg_id = reg_id)
        #     if not len(instance):
        #         instance = FCMDevice.objects.filter(dev_id = dev_id)
        #         if not len(instance):    
        #             raise Exception
        #     if request.user.id == None:
        #         instance.update(user = request.user,is_active = True,name=request.user.username,dev_id=dev_id,device_type = request.POST.get('device_type'),reg_id=reg_id)
        #     else:
        #         instance.update(is_active = True,dev_id=request.POST.get('dev_id'),device_type = request.POST.get('device_type'), reg_id=reg_id)    
        #     return JsonResponse({"status":"Success"},safe = False)
        # except Exception as e:
        #     if request.user:
        #         try:
        #             instance = FCMDevice.objects.create(user = request.user,reg_id = request.POST.get('reg_id'),name=request.user.username,dev_id=request.POST.get('dev_id'),device_type = request.POST.get('device_type'))
        #         except Exception as e1:
        #             instance = FCMDevice.objects.create(reg_id = request.POST.get('reg_id'),name='Anonymous',dev_id=request.POST.get('dev_id'),device_type = request.POST.get('device_type'))
        #     else:
        #         instance = FCMDevice.objects.create(reg_id = request.POST.get('reg_id'),name='Anonymous',dev_id=request.POST.get('dev_id'),device_type = request.POST.get('device_type'))
        #     return JsonResponse({"status":"Success"},safe = False)


    def remove_device(self,request):
        try:
            instance = FCMDevice.objects.filter(reg_id = request.POST.get('reg_id'), is_active = True, user = request.user,dev_id=request.POST.get('dev_id'))
            if not len(instance):
                raise Exception
            instance.update(is_active = False)
            return JsonResponse({"status":"Success"},safe = False)
        except Exception as e:
            return JsonResponse({"status":"Failed","message":"Device not found for this user"},safe = False)


language_options = (
    ('0', "All"),
    ('1', "English"),
    ('2', "Hindi"),
    ('3', "Tamil"),
    ('4', "Telgu"),
)

user_group_options = (
    ('0', "All"),
    ('1', "Installed but did not sign up till 3 hours"),
    ('2', "Installed and never signed up"),
    ('3', "Signed up but never played a video"),
    ('4', "Signed up but no opening of app since 24 hours"),
    ('5', "Signed up but no opening of app since 72 hours "),
    ('6', "Never created a video"),
)

notification_type_options = (
    ('0', "video page"),
    ('1', "user"),
    ('2', "category"),
    ('3', "hashtag"),
    ('4', "Announcements"),
)

status_options = (
    ('0', "Not Opened"),
    ('1', "Opened"),
)

class PushNotification(RecordTimeStamp):

    title = models.CharField(_('title'),max_length=100,null=True,blank=True)
    description = models.CharField(_('description'),max_length=100,null=True,blank=True)
    language = models.CharField(choices=language_options, blank = True, null = True, max_length=10, default='0')
    notification_type = models.CharField(choices=notification_type_options, blank = True, null = True, max_length=10, default='4')
    instance_id = models.CharField('instance_id', blank = True, null = True, max_length=40, default='')
    user_group = models.CharField(choices=user_group_options, blank = True, null = True, max_length=10, default='0')
    scheduled_time = models.DateTimeField(auto_now=False,auto_now_add=True,blank=False,null=False)
    is_scheduled = models.BooleanField(default=False)
    is_removed = models.BooleanField(default=False)
    is_executed = models.BooleanField(default=False)
    repeated_hour = models.PositiveIntegerField(null=True,blank=True,default=0)
    
class PushNotificationUser(RecordTimeStamp):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, related_name='push_notification_user',editable=False)
    push_notification_id = models.ForeignKey(PushNotification, blank = True, null = True, related_name='push_notification_id',editable=False)
    status = models.CharField(choices=status_options, blank = True, null = True, max_length=10, default='0')

