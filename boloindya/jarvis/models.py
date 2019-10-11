# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.template.defaultfilters import slugify

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