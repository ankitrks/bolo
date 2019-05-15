# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from datetime import timedelta

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from ..core.conf import settings
from ..core.utils.models import AutoSlugField

class RecordTimeStamp(models.Model):
    created_at=models.DateTimeField(auto_now=False,auto_now_add=True,blank=False,null=False) # auto_now will add the current time and date whenever field is saved.
    last_modified=models.DateTimeField(auto_now=True,auto_now_add=False)                     # while auto_now_add will save the date and time only when record is first created
    class Meta:
        abstract = True

language_options = (
    ('1', "English"),
    ('2', "Hindi"),
    ('3', "Tamil"),
    ('4', "Telgu"),
)
refrence_options = (
    ('0', "native"),
    ('1', "facebook"),
)

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_("profile"), related_name='st',editable=False)

    slug = AutoSlugField(populate_from="user.username", db_index=False, blank=True)
    location = models.CharField(_("location"), max_length=75, blank=True)
    last_seen = models.DateTimeField(_("last seen"), auto_now=True)
    last_ip = models.GenericIPAddressField(_("last ip"), blank=True, null=True)
    timezone = models.CharField(_("time zone"), max_length=32, default='UTC')
    is_administrator = models.BooleanField(_('administrator status'), default=False)
    is_moderator = models.BooleanField(_('moderator status'), default=False)
    is_verified = models.BooleanField(_('verified'), default=False,
                                      help_text=_('Designates whether the user has verified his '
                                                  'account by email or by other means. Un-select this '
                                                  'to let the user activate his account.'))

    topic_count = models.PositiveIntegerField(_("topic count"), default=0)
    comment_count = models.PositiveIntegerField(_("comment count"), default=0)

    last_post_hash = models.CharField(_("last post hash"), max_length=32, blank=True)
    last_post_on = models.DateTimeField(_("last post on"), null=True, blank=True)
    # new  profile fields:{maaz} #
    profile_pic = models.CharField(_("Profile Pic"), max_length=1000, blank=True)
    name = models.CharField(_("Name"), max_length=100, blank=True)
    bio = models.CharField(_("Bio"), max_length=300, blank=True)
    about = models.CharField(_("About"), max_length=500, blank=True)
    language = models.CharField(choices=language_options, blank = True, null = True, max_length=10, default='1')
    sub_category=models.ManyToManyField('forum_category.Category', verbose_name=_("Sub Category"),related_name='%(app_label)s_%(class)s_sub_category')
    refrence = models.CharField(choices=refrence_options, blank = True, null = True, max_length=10,default='0')
    extra_data = models.TextField(null=True,blank=True)
    social_identifier = models.CharField(_("Social Identifier"), max_length=100, blank=True)
    mobile_no = models.CharField(_("Mobile No"), max_length=100, blank = True, null = True)
    follow_count = models.PositiveIntegerField(null=True,blank=True,default=0)
    follower_count = models.PositiveIntegerField(null=True,blank=True,default=0)
    question_count = models.PositiveIntegerField(null=True,blank=True,default=0)
    answer_count = models.PositiveIntegerField(null=True,blank=True,default=0)
    share_count = models.PositiveIntegerField(null=True,blank=True,default=0)
    like_count = models.PositiveIntegerField(null=True,blank=True,default=0)
    bolo_score = models.PositiveIntegerField(null=True,blank=True,default=0)

    # end #

    class Meta:
        verbose_name = _("forum profile")
        verbose_name_plural = _("forum profiles")

    def save(self, *args, **kwargs):
        if self.user.is_superuser:
            self.is_administrator = True

        if self.is_administrator:
            self.is_moderator = True

        super(UserProfile, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('spirit:user:detail', kwargs={'pk': self.user.pk, 'slug': self.slug})

    def update_post_hash(self, post_hash):
        assert self.pk

        # Let the DB do the hash
        # comparison for atomicity
        return bool(UserProfile.objects
                    .filter(pk=self.pk)
                    .exclude(
                        last_post_hash=post_hash,
                        last_post_on__gte=timezone.now() - timedelta(
                            minutes=settings.ST_DOUBLE_POST_THRESHOLD_MINUTES))
                    .update(
                        last_post_hash=post_hash,
                        last_post_on=timezone.now()))
        def __unicode__(self):
            return self.slug

class Follower(RecordTimeStamp):
    user_following = models.ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, related_name='user_following')# User being Followed
    user_follower = models.ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, related_name='user_follower')# User Start Following
    is_active = models.BooleanField(default = True)

    class Meta:
        verbose_name_plural = 'User\'s Followers'

    def __unicode__(self):
            return str(self.user_following)


class Weight(RecordTimeStamp):
    features=models.CharField(max_length=20)
    weight= models.FloatField(default=0,null=True)

    def __unicode__(self):
        return self.features

class AppVersion(RecordTimeStamp):
    app_name = models.CharField(_("Name"), max_length=100, blank=True)
    app_version = models.CharField(_("Version"), max_length=100, blank=True)
    is_hard_push = models.BooleanField(default = False)
    changes_title = models.CharField(_("Changes Title"), max_length=225, null=True,blank=True)
    changes = models.TextField(_("Changes"),null=True,blank=True)


    class Meta:
        verbose_name_plural = 'AppVersions'

    def __unicode__(self):
            return str(self.app_name)
