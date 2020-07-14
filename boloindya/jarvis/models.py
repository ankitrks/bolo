# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.template.defaultfilters import slugify
from fcm.models import AbstractDevice
from django.http import JsonResponse
from forum.category.models import Category
from django.db.models import Q
from forum.topic.models import RecordTimeStamp,Topic,UserInfo
from drf_spirit.utils import language_options
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from datetime import datetime
from forum.topic.utils import update_redis_fcm_device_entries

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
    is_topic = models.BooleanField(default=False)
    topic = models.ForeignKey(Topic,null=True,blank=True)
    uploaded_user = models.ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, related_name='%(app_label)s_%(class)s_user',editable=False)
    
    def __unicode__(self):
        return str(self.filename_uploaded)

    def save(self, *args, **kwargs):
        if self.video_title:
            self.slug= slugify(self.video_title)
        super(VideoUploadTranscode, self).save(*args, **kwargs)

device_options = (
    ('1', "Android"),
    ('2', "iOS"),
    ('3', "Web"),
)

import json
from datetime import datetime

class FCMDevice(AbstractDevice):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, related_name='%(app_label)s_%(class)s_user',editable=False)
    device_type = models.CharField(choices=device_options, blank = True, null = True, max_length=10, default='0')
    created_at=models.DateTimeField(auto_now=False,auto_now_add=True,blank=False,null=False) # auto_now will add the current time and date whenever field is saved.
    last_modified=models.DateTimeField(auto_now=True,auto_now_add=False)                     # while auto_now_add will save the date and time only when record is first created
    is_uninstalled=models.BooleanField(default=False)
    uninstalled_date=models.DateTimeField(auto_now=False,auto_now_add=False,blank=True,null=True)
    uninstalled_desc=models.TextField(null=True,blank=True)
    device_model = models.CharField(blank = True, null = True, max_length=100, default='')
    current_version = models.CharField(blank = True, null = True, max_length=100, default='')
    manufacturer = models.CharField(blank = True, null = True, max_length=50, default='')
    start_time = models.DateTimeField(auto_now=False,auto_now_add=False,blank=True,null=True)
    end_time = models.DateTimeField(auto_now=False,auto_now_add=False,blank=True,null=True)
    current_activity=models.CharField(blank = True, null = True, max_length=100, default='')

    def __unicode__(self):
        return str(self.user)


    def register_device(self,request):
        reg_id = request.POST.get('reg_id')
        dev_id=request.POST.get('dev_id')
        device_model=request.POST.get('device_model', '')
        current_version=request.POST.get('current_version', '')
        manufacturer=request.POST.get('manufacturer', '')
        data_dict = {'reg_id':reg_id, 'dev_id':dev_id,'device_model':device_model,\
         'current_version':current_version, 'manufacturer':manufacturer, 'user_id':request.user.id,\
         'device_type':request.POST.get('device_type',None),'created_at':datetime.now() }
        if dev_id:
            update_redis_fcm_device_entries(dev_id,data_dict)
        return JsonResponse({"status":"Success"},safe = False)
        try:
            instance = FCMDevice.objects.using('default').filter(Q(reg_id = reg_id) | Q(dev_id = dev_id))
            if not len(instance):
                print 'Not Exists'
                raise Exception
            print 'Exisits'
            desc=instance[0].uninstalled_desc
            if desc:
                list_data = json.loads(desc)
                if 'uninstall' in list_data[len(list_data)-1]:
                    list_data.append({'install': datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                desc=json.dumps(list_data)
            if request.user.id == None:
                instance.update(is_active = True,dev_id=dev_id,device_type = request.POST.get('device_type'), reg_id=reg_id, is_uninstalled=False, uninstalled_desc=desc, device_model=device_model, current_version=current_version, manufacturer=manufacturer) 
            else:
                instance.update(user = request.user,is_active = True,name=request.user.username,dev_id=dev_id,device_type = request.POST.get('device_type'),reg_id=reg_id , is_uninstalled=False, uninstalled_desc=desc, device_model=device_model, current_version=current_version, manufacturer=manufacturer)
            return JsonResponse({"status":"Success"},safe = False)
        except Exception as e:
            if request.user.id == None:
                instance = FCMDevice.objects.create(reg_id = request.POST.get('reg_id'),name='Anonymous',dev_id=request.POST.get('dev_id'),device_type = request.POST.get('device_type'), is_uninstalled=False, device_model=device_model, current_version=current_version, manufacturer=manufacturer)
            else:
                instance = FCMDevice.objects.create(user = request.user,reg_id = request.POST.get('reg_id'),name=request.user.username,dev_id=request.POST.get('dev_id'),device_type = request.POST.get('device_type'), is_uninstalled=False, device_model=device_model, current_version=current_version, manufacturer=manufacturer)
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



user_group_options = (
    ('0', "All"),
    ('1', "Installed but did not sign up till 3 hours"),
    ('2', "Installed and never signed up"),
    ('3', "Signed up but never played a video"),
    ('4', "Signed up but no opening of app since 24 hours"),
    ('5', "Signed up but no opening of app since 72 hours "),
    ('6', "Never created a video"),
    ('7', "Test User"),
    ('8', "Particular User"),
    ('9', 'Creators'),
    ('10', 'Active Users')
)

notification_type_options = (
    ('0', "video page"),
    ('1', "user"),
    ('2', "category"),
    ('3', "hashtag"),
    ('4', "Announcements"),
    ('5', "Create Video Byte"),
)

status_options = (
    ('0', "Not Opened"),
    ('1', "Opened"),
    ('2', 'Sent')
)

metrics_options = (
    ('0', "Video Created"),
    ('1', "Video Views"),
    ('2', "Bolo Actions"),
    ('3', "Video Shares"),
    ('4', "New Video Creators"),
    ('5', "Number of Installs"),
    ('6', "DAU"),
    ('7', "Unique Video Views"),
    ('8', "MAU"),
    ('9', 'Total Video Creators'),
    ('10', 'Install-Signup Map'),
    ('11', 'Uninstalls'),
    ('12', 'PlayTime'),
    ('13', "Video Shares (Telegram)"),
)

metrics_slab_options = (
    ('0', "5 to 24"),
    ('1', "25 to 59"),
    ('2', "60 or more"),
    ('3', "Likes"),
    ('4', "Comments"),
    ('5', "Shares"),
    ('6', "Organic"),
    ('7', "Paid"),
    ('t', "Total"),
    ('9', 'Less than 5'),
)

metrics_language_options = language_options

# all_category_list = Category.objects.all()
# category_slab_options = []

# for item in all_category_list:
#     category_slab_options.append((str(item.pk), str(item.title)))

# category_slab_options = tuple(category_slab_options)


class DashboardMetrics(RecordTimeStamp):
    metrics = models.CharField(choices = metrics_options, blank = True, null = True, max_length = 10, default = '0')
    metrics_slab = models.CharField(choices = metrics_slab_options, blank = True, null = True, max_length = 10, default = None)
    date = models.DateTimeField(auto_now = False, auto_now_add = False, blank = False, null = False)
    week_no = models.PositiveIntegerField(null = True, blank = True, default = 0)
    count = models.BigIntegerField(null = True, blank = True, default = 0)

    class Meta:
        ordering = ['date']
        
    def __unicode__(self):
        return str(self.id)


# new field added and diff from DashBoardMetrics model
class DashboardMetricsJarvis(RecordTimeStamp):
    metrics = models.CharField(choices = metrics_options, blank = True, null = True, max_length = 10, default = '0')
    metrics_language_options = models.CharField(choices = language_options, blank = True, null = True, max_length = 10, default = '0')
    category = models.ForeignKey('forum_category.Category', verbose_name =_("category"), related_name = "%(app_label)s_%(class)s_category" ,null = True, blank = True)
    #category_slab_options = models.CharField(choices = category_slab_options, blank = True, null = True, max_length = 10, default = '0')
    metrics_slab = models.CharField(choices = metrics_slab_options, blank = True, null = True, max_length = 10, default = None)
    date = models.DateTimeField(auto_now = False, auto_now_add = False, blank = False, null = False)
    week_no = models.PositiveIntegerField(null = True, blank = True, default = 0)
    count = models.PositiveIntegerField(null = True, blank = True, default = 0)

    class Meta:
        ordering = ['date']
        
    def __unicode__(self):
        return str(self.id)



class PushNotification(RecordTimeStamp):
    title = models.CharField(_('title'),max_length=200,null=True,blank=True)
    description = models.CharField(_('description'),max_length=500,null=True,blank=True)
    language = models.CharField(choices=language_options, blank = True, null = True, max_length=10, default='0')
    notification_type = models.CharField(choices=notification_type_options, blank = True, null = True, max_length=10, default='4')
    instance_id = models.CharField('instance_id', blank = True, null = True, max_length=40, default='')
    category = models.ForeignKey('forum_category.Category', verbose_name=_("category"), related_name="category_notification",null=True,blank=True)
    m2mcategory = models.ManyToManyField('forum_category.Category', verbose_name=_("category"), related_name="m2mcategories_notification",blank=True)
    user_group = models.CharField(choices=user_group_options, blank = True, null = True, max_length=10, default='0')
    scheduled_time = models.DateTimeField(auto_now=False,auto_now_add=True,blank=False,null=False)
    is_scheduled = models.BooleanField(default=False)
    image_url = models.CharField(_('image_url'),max_length=1000,null=True,blank=True)
    is_removed = models.BooleanField(default=False)
    is_executed = models.BooleanField(default=False)
    days_ago = models.PositiveIntegerField(null=True,blank=True,default=0)
    particular_user_id=models.CharField(_('particular_user_id'),max_length=20,null=True,blank=True)
    repeated_hour = models.PositiveIntegerField(null=True,blank=True,default=0)

class PushNotificationUser(RecordTimeStamp):

    user=models.ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, related_name='push_notification_user',editable=False)
    device=models.ForeignKey(FCMDevice, blank = True, null = True, related_name='push_notification_device',editable=False)
    push_notification_id = models.ForeignKey(PushNotification, blank = True, null = True, related_name='push_notification_id',editable=False)
    status = models.CharField(choices=status_options, blank = True, null = True, max_length=10, default='0')
    response_dump = models.TextField(null=True,blank=True)

class StateDistrictLanguage(RecordTimeStamp):
    state_name = models.CharField(_('State Name'),max_length=200,null=True,blank=True)
    district_name = models.CharField(_('District Name'),max_length=200,null=True,blank=True)
    state_language = models.CharField(choices=language_options,blank=True,null=True,max_length=10,default='1')
    district_language = models.CharField(choices=language_options,blank=True,null=True,max_length=10,default='1')
    response_dump = models.TextField(null=True,blank=True)

    class Meta:
        verbose_name = _("State District Language")
        verbose_name_plural = _("State District Languages")

    def __unicode__(self):
        return str(self.district_name)+"--"+str(self.district_language)

    def save(self, *args, **kwargs):
        if not self.district_language:
            self.district_language = self.state_language
        super(StateDistrictLanguage, self).save(*args, **kwargs)


class BannerUser(RecordTimeStamp):

    user=models.ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, related_name='banner_user',editable=False)
    term = models.CharField(_('term'),max_length=1000,null=True,blank=True)
    response_type = models.CharField(_("Response Type"),null=True,blank=True,max_length=255)

    class Meta:
        verbose_name = _("Banner User")
        verbose_name_plural = _("Banner Users")

    def __unicode__(self):
        return self.term

class UserCountNotification(RecordTimeStamp):

    language = models.CharField(choices=language_options, blank = True, null = True, max_length=10, default='0')
    user_group = models.CharField(choices=user_group_options, blank = True, null = True, max_length=10, default='0')
    category = models.ForeignKey('forum_category.Category', verbose_name=_("category"), related_name="user_count_notification_category",null=True,blank=True)
    no_of_user = models.PositiveIntegerField(null=True,blank=True,default=0)
    fcm_users = models.TextField(null=True) 

    class Meta:
        verbose_name = _("UserCountNotification")
        verbose_name_plural = _("UserCountNotifications")

class Report(RecordTimeStamp):
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Reported By"),related_name="reported_by", null=True,blank=True,editable=False)
    report_type = models.CharField(_("report_type"), max_length=100,null=True,blank=True)
    is_moderated = models.BooleanField(default=False)
    target_type = models.ForeignKey(ContentType, verbose_name=('target type'),null=True,blank=True)
    target_id = models.PositiveIntegerField(('object ID'),null=True,blank=True)
    target = GenericForeignKey('target_type', 'target_id')
    moderated_on = models.DateTimeField(blank=True,null=True)
    moderated_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Moderated By"),related_name="report_moderated_by", null=True,blank=True,editable=False)
    is_active = models.BooleanField(default = True)

    def __unicode__(self):
        return str(self.topic)

    def remove_post_or_block_user_temporarily(self,moderated_by=None):
        if isinstance(self.target, Topic):
            instance = self.target
            instance.is_removed = True
            instance.save()
        else:
            instance = self.target
            instance.is_active = False
            instance.save()
        Report.objects.filter(target_id=self.target_id, target_type_id=self.target_type_id).update(is_moderated = True, is_active=False, moderated_by = moderated_by, moderated_on = datetime.now())
        return True

    def seems_fine(self,moderated_by=None):
        Report.objects.filter(target_id=self.target_id, target_type_id=self.target_type_id).update(is_moderated = True, is_active=False, moderated_by = moderated_by, moderated_on = datetime.now())
        return True

    def unremove_video_or_unblock(self,moderated_by=None):
        if isinstance(self.target, Topic):
            instance = self.target
            instance.is_removed = False
            instance.save()
        else:
            instance = self.target
            instance.is_active = True
            instance.save()
        Report.objects.filter(target_id=self.target_id, target_type_id=self.target_type_id).update(is_moderated = True, is_active=False, moderated_by = moderated_by, moderated_on = datetime.now())



