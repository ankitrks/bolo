# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

# Create your models here.
class VideoUploadTranscode(models.Model):
    s3_file_url = models.CharField(_("S3 File URL"),null=True,blank=True,max_length=1000)
    transcoded_file_url = models.CharField(_("Transcoded File URL"),null=True,blank=True,max_length=1000)
    transcode_job_id = models.TextField(_("Transcode Job ID"), blank = True)
    transcode_dump = models.TextField(_("Transcode Dump"), blank = True)
    filename_uploaded = models.CharField(_("Filename Uploaded"),null=True,blank=True,max_length=1000)
    filename_changed = models.CharField(_("Filename changed"),null=True,blank=True,max_length=1000)
    folder_to_upload = models.CharField(_("Filename changed"),null=True,blank=True,max_length=1000)
    folder_to_upload_changed = models.CharField(_("Filename changed"),null=True,blank=True,max_length=1000)

    def __unicode__(self):
        return self.filename_uploaded