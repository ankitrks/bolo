# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from datetime import timedelta,datetime

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from ..core.conf import settings
from ..core.utils.models import AutoSlugField
from tinymce.models import HTMLField
from drf_spirit.utils import language_options,month_choices, salary_choices
from django.db.models import F,Q
from diff_model import ModelDiffMixin

class RecordTimeStamp(models.Model):
    created_at=models.DateTimeField(auto_now=False,auto_now_add=True,blank=False,null=False) # auto_now will add the current time and date whenever field is saved.
    last_modified=models.DateTimeField(auto_now=True,auto_now_add=False)                     # while auto_now_add will save the date and time only when record is first created
    class Meta:
        abstract = True


gender_option = (
    ('1', "Male"),
    ('2', "Female"),
    ('3', "Other"),
)

refrence_options = (
    ('0', "native"),
    ('1', "facebook"),
)



class UserProfile(models.Model,ModelDiffMixin):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_("profile"), related_name='st', editable=False)
    slug = models.CharField(_("slug"), max_length=100, db_index=True, blank=True)
    location = models.CharField(_("location"), max_length=75, blank=True)
    last_seen = models.DateTimeField(_("last seen"), auto_now=True)
    last_ip = models.GenericIPAddressField(_("last ip"), blank=True, null=True)
    timezone = models.CharField(_("time zone"), max_length=32, default='UTC')
    is_expert = models.BooleanField(_('expert status'), default=False)
    is_administrator = models.BooleanField(_('administrator status'), default=False)
    is_moderator = models.BooleanField(_('moderator status'), default=False)
    is_verified = models.BooleanField(_('verified'), default=False,
                                      help_text=_('Designates whether the user has verified his '
                                                  'account by email or by other means. Un-select this '
                                                  'to let the user activate his account.'))

    topic_count = models.PositiveIntegerField(_("topic count"), default=0)
    comment_count = models.PositiveIntegerField(_("comment count"), default=0)
    is_popular = models.BooleanField(_('Is Popular'),default = False)
    is_superstar = models.BooleanField(_('Is Superstar'),default = False)
    is_business = models.BooleanField(_('Is Business'),default = False)

    last_post_hash = models.CharField(_("last post hash"), max_length=32, blank=True)
    last_post_on = models.DateTimeField(_("last post on"), null=True, blank=True)
    cover_pic = models.CharField(_("Cover Pic"), max_length=1000, blank=True)
    # new  profile fields:{maaz} #
    profile_pic = models.CharField(_("Profile Pic"), max_length=1000, blank=True)
    name = models.CharField(_("Name"), max_length=100, blank=True,db_index=True)
    bio = models.CharField(_("Bio"), max_length=300, blank=True)
    d_o_b = models.CharField(_("Date of Birth"), max_length=100, blank=True, null = True)
    gender = models.CharField(choices=gender_option, blank = True, null = True, max_length=10, default='')
    about = models.CharField(_("About"), max_length=500, blank=True)
    language = models.CharField(choices=language_options, blank = True, null = True, max_length=10, default='1',db_index=True)
    sub_category=models.ManyToManyField('forum_category.Category', verbose_name=_("Sub Category"),related_name='%(app_label)s_%(class)s_sub_category')
    refrence = models.CharField(choices=refrence_options, blank = True, null = True, max_length=10,default='0')
    extra_data = models.TextField(null=True,blank=True)
    social_identifier = models.CharField(_("Social Identifier"), max_length=100, blank=True)
    mobile_no = models.CharField(_("Mobile No"), max_length=100, blank = True, null = True, db_index = True)
    follow_count = models.PositiveIntegerField(null=True,blank=True,default=0,db_index=True)
    follower_count = models.PositiveIntegerField(null=True,blank=True,default=0,db_index=True)
    question_count = models.PositiveIntegerField(null=True,blank=True,default=0)
    answer_count = models.PositiveIntegerField(null=True,blank=True,default=0)
    share_count = models.PositiveIntegerField(null=True,blank=True,default=0)
    like_count = models.PositiveIntegerField(null=True,blank=True,default=0)
    vb_count = models.PositiveIntegerField(null=True,blank=True,default=0,db_index=True)
    view_count = models.BigIntegerField(null=True,blank=True,default=0,db_index=True)
    own_vb_view_count = models.BigIntegerField(null=True,blank=True,default=0,db_index=True)
    bolo_score = models.PositiveIntegerField(null=True,blank=True,default=0,db_index=True)
    encashable_bolo_score = models.PositiveIntegerField(null=True,blank=True,default=0)
    is_geo_location = models.BooleanField(default=False)
    lat = models.CharField(_('Latitude'), blank=True, null=True, max_length = 50, default = '')
    lang = models.CharField(_('Langitude'), blank=True, null=True, max_length = 50, default = '')
    is_test_user = models.BooleanField(default=False)

    linkedin_url = models.CharField(_("LinkedIn URL"), max_length=200, blank=True, null = True)
    twitter_id = models.CharField(_("Twitter ID"), max_length=200, blank=True, null = True)
    instagarm_id = models.CharField(_("Instagram ID"), max_length=200, blank=True, null = True)

    click_id = models.CharField(_("Click Id"), max_length=300, blank=True)
    click_id_response = models.TextField(_("Click Id Response"),null=True, blank=True)
    is_dark_mode_enabled = models.BooleanField(default=False)
    total_vb_playtime = models.PositiveIntegerField(null=True,blank=True,default=0,db_index=True)
    total_time_spent = models.PositiveIntegerField(null=True,blank=True,default=0,db_index=True)
    state_name = models.CharField(_('State Name'),max_length=200,null=True,blank=True)
    city_name = models.CharField(_('City Name'),max_length=200,null=True,blank=True)
    paytm_number = models.CharField(_("Mobile No"), max_length=100, blank = True, null = True)
    android_did = models.CharField(_('android_did'),max_length=200,null=True,blank=True)
    is_guest_user = models.BooleanField(default=False)
    boost_views_count = models.PositiveIntegerField(_("Boost View"), null=True, blank=True, default=0)
    boost_like_count = models.PositiveIntegerField(_("Boost Like"), null=True, blank=True, default=0)
    boost_follow_count = models.PositiveIntegerField(_("Boost Follow"), null=True, blank=True, default=0)
    boosted_time = models.DateTimeField(null=True, blank=True)
    boost_span = models.PositiveIntegerField(_("Boost Span(Hours)"), null=True, blank=True, default=0)
    country_code = models.CharField(_("Country Phone Code"), max_length=20, blank = True, null = True)
    salary_range = models.CharField(choices=salary_choices, blank = True, null = True, max_length=10,db_index=True)
    is_insight_fix = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("user profile")
        verbose_name_plural = _("user profiles")

    def save(self, *args, **kwargs):
        if self.user.is_superuser:
            self.is_administrator = True

        if self.is_administrator:
            self.is_moderator = True

        super(UserProfile, self).save(*args, **kwargs)
        if self.has_changed and ('is_popular' in self.changed_fields or 'is_superstar' in self.changed_fields):
            from drf_spirit.utils import add_bolo_score,reduce_bolo_score
            if 'is_popular' in self.changed_fields:
                if self.get_field_diff('is_popular')[1]:
                    add_bolo_score(self.user_id,'is_popular',self)
                else:
                    reduce_bolo_score(self.user_id,'is_popular',self)
            if 'is_superstar' in self.changed_fields:
                if self.get_field_diff('is_superstar')[1]:
                    add_bolo_score(self.user_id,'is_superstar',self)
                else:
                    reduce_bolo_score(self.user_id,'is_superstar',self)


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

def current_year():
    return datetime.now().year

def previous_month():
    if datetime.now().month ==1:
        return 12
    else:
        return datetime.now().month-1

class UserPay(RecordTimeStamp):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, related_name='user_pay')
    for_year = models.PositiveIntegerField(_('year'), choices=((r,r) for r in range(2019, datetime.now().year+1)), default=current_year)
    for_month = models.PositiveIntegerField(_('month'),choices=month_choices,default =previous_month )
    pay_date = models.DateTimeField(_("Pay Date"), null = True, blank = False)
    amount_pay = models.PositiveIntegerField(_("Amount Payed"), null = True, blank = False,default=0)
    transaction_id = models.CharField(max_length=50,null=True,blank=True)
    total_video_created = models.PositiveIntegerField(_("Total Videos Created"), null = True, blank = False,default=0)
    videos_in_language = models.TextField(null=True,blank=True)
    total_monetized_video = models.PositiveIntegerField(_("Total Monetized Videos"), null = True, blank = False,default=0)
    left_for_moderation = models.PositiveIntegerField(_("Left For Moderation"), null = True, blank = False,default=0)
    total_like = models.PositiveIntegerField(_("Total Likes"), null = True, blank = False,default=0)
    total_comment = models.PositiveIntegerField(_("Total Comments"), null = True, blank = False,default=0)
    total_view = models.PositiveIntegerField(_("Total Views"), null = True, blank = False,default=0)
    total_share = models.PositiveIntegerField(_("Total Shares"), null = True, blank = False,default=0)
    total_bolo_score_earned = models.PositiveIntegerField(_("Total Views"), null = True, blank = False,default=0)
    bolo_bifurcation = models.TextField(null=True,blank=True)
    is_evaluated = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    is_active = models.BooleanField(default = True)

    class Meta:
        verbose_name_plural = 'User\'s Pay'

    def __unicode__(self):
        return str(self.user)



class OldMonthInsightData(RecordTimeStamp):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, related_name='user_insight_data')
    for_year = models.PositiveIntegerField(_('year'), choices=((r,r) for r in range(2019, datetime.now().year+1)), default=current_year)
    for_month = models.PositiveIntegerField(_('month'),choices=month_choices,default =previous_month )
    insight_data = models.TextField(null=True,blank=True)

    def __unicode__(self):
        return str(self.user)+' - '+str(self.get_for_month_display())+' - '+str(self.get_for_year_display())
    

class InsightDataDump(RecordTimeStamp):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, related_name='insight_dump')
    for_year = models.PositiveIntegerField(_('year'), choices=((r,r) for r in range(2019, datetime.now().year+1)), null=True,blank = True)
    for_month = models.PositiveIntegerField(_('month'),choices=month_choices,null=True,blank=True )
    old_insight_data = models.TextField(null=True,blank=True)
    new_insight_data = models.TextField(null=True,blank=True)

    class Meta:
        verbose_name_plural = 'InsightDataDump\'s'

    def __unicode__(self):
        return str(self.user)+' - '+str(self.get_for_month_display())+' - '+str(self.get_for_year_display())



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
    is_monetize = models.BooleanField(default=False)
    bolo_score = models.PositiveIntegerField(_('Minimum Bolo Score For Monetize/Bolo Score Equivalent Money'),null=True,blank=True,default=0)
    equivalent_INR = models.PositiveIntegerField(_('Bolo Equivalent Money in INR'),null=True,blank=True,default=0)

    def __unicode__(self):
        return self.features

class AndroidLogs(RecordTimeStamp):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("profile"), related_name='st_logs',editable=False, blank=True, null=True)
    logs = models.TextField(_("Android Logs"),null=True, blank=True)
    log_type = models.CharField(_("Log Type"),null=True,blank=True,max_length=255)
    is_executed = models.BooleanField(_("is_executed"), default=False)
    android_id = models.CharField(_("android_id"), max_length=100, blank=True, null = True, editable = False)

    def __unicode__(self):
        return str(self.user)

# class recording the playime for videos
class VideoPlaytime(models.Model):
    from forum.topic.models import Topic    

    user = models.CharField(_("user"), null = True, blank = True, max_length = 250, db_index = True)
    videoid = models.CharField(_("videoid"), null = True, blank = True, max_length = 250, db_index = True)
    playtime = models.PositiveIntegerField(_("playtime"), default=0)
    timestamp = models.DateTimeField(_("timestamp"), null = True, blank = False)
    # created_at = models.DateTimeField(_("created_at"), null = True, blank = False)
    video = models.ForeignKey(Topic, null=True, blank=True)

# class recording the fraction of videos played
class VideoCompleteRate(models.Model):

    user = models.CharField(_("user"), null = True, blank = False, max_length = 250, db_index = True)
    videoid = models.CharField(_("videoid"), null = True, blank = False, max_length = 250, db_index = True)
    duration = models.PositiveIntegerField(_("duration"), default = 0)
    playtime = models.PositiveIntegerField(_("playtime"), default = 0)
    percentage_viewed = models.DecimalField(_("percentage_viewed"), max_digits = 5, decimal_places = 2)
    timestamp = models.DateTimeField(_("timestamp"), null = True, blank = False)
    # created_at = models.DateTimeField(_("created_at"), null = True, blank = False)

# class storing the total time spend by the user on the app
class UserAppTimeSpend(models.Model):

    user = models.CharField(_("user"), null = True, blank = False, max_length = 250, db_index = True)
    total_time = models.DecimalField(_("totaltime"), max_digits = 5, decimal_places = 2)
    reference_time = models.DateTimeField(_("reference_time"), null = True, blank = False)


class AppVersion(RecordTimeStamp):
    app_name = models.CharField(_("Name"), max_length=100, blank=True)
    app_version = models.CharField(_("Version"), max_length=100, blank=True)
    version_to_be_pushed = models.CharField(_("Version To be Pushed"), max_length=100, blank=True)
    is_hard_push = models.BooleanField(default = False)
    changes_title = models.CharField(_("Changes Title"), max_length=225, null=True,blank=True)
    changes = models.TextField(_("Changes"),null=True,blank=True)


    class Meta:
        verbose_name_plural = 'AppVersions'

    def __unicode__(self):
        return str(self.app_name)

class AppPageContent(RecordTimeStamp):
    page_name = models.CharField(_("Page Name"),max_length=100,blank=True)
    page_description = HTMLField(_("Page Description"), null=True, blank=True)

    def __unicode__(self):
        return str(self.page_name)

class ReferralCode(RecordTimeStamp):
    code = models.CharField(_("Ref Code"), max_length=20, blank=True, db_index = True)
    for_user = models.ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, editable = False)
    purpose = models.CharField(_("Purpose"), max_length=50, blank=True)
    campaign_url = models.CharField(_("Playstore URL"), max_length=350, blank=True, null = True, editable = False)
    is_active = models.BooleanField(_("live"), default = True)
    is_refer_earn_code = models.BooleanField(_("Is Refer Earn Code?"), default = False)
    download_count = models.PositiveIntegerField(_("ownload count"), default=0)
    signup_count = models.PositiveIntegerField(_("signup count"), default=0)

    def __unicode__(self):
        return str(self.code)

    def save(self, *args, **kwargs):
        self.campaign_url = 'https://play.google.com/store/apps/details?id=com.boloindya.boloindya&referrer=utm_source%3D' + self.code + '%26utm_medium%3D' + self.code + '%26utm_content%3Dvaun%26utm_campaign%3Dcpc%26anid%3Dadmob'
        super(ReferralCode, self).save(*args, **kwargs)

    def playstore_url(self):
        return '<b>playstore URL - </b> https://play.google.com/store/apps/details?id=com.boloindya.boloindya&referrer=utm_source%3D' + self.code + '%26utm_medium%3D' + self.code + '%26utm_content%3Dvaun%26utm_campaign%3Dcpc%26anid%3Dadmob'
    playstore_url.allow_tags = True

    def no_playstore_url(self):
        return '<b>non playstore url - </b> https://www.boloindya.com/download/?id=com.boloindya.boloindya&referrer=utm_source%3D' + self.code + '%26utm_medium%3D' + self.code + '%26utm_content%3Dvaun%26utm_campaign%3Dcpc%26anid%3Dadmob'
    no_playstore_url.allow_tags = True

    def downloads_list(self):
        return ReferralCodeUsed.objects.filter(code = self, is_download = True, by_user__isnull = True)

    def signup_list(self):
        return ReferralCodeUsed.objects.filter(code = self, is_download = True, by_user__isnull = False)

    def downloads(self):
        return self.downloads_list().distinct('android_id').count()

    def signup(self):
        return self.signup_list().distinct('by_user').count()

    def referral_url(self):
        return 'https://www.boloindya.com/invite/'+self.for_user.username+'/'+str(self.for_user.id)+'/'

class ReferralCodeUsed(RecordTimeStamp):
    code = models.ForeignKey(ReferralCode, blank=False, null = False, related_name = 'refcode')
    by_user = models.ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True )
    is_download = models.BooleanField(default = True)
    click_id = models.CharField(_("Click Id"), max_length=255, blank=True)
    pid = models.CharField(_("PID"), max_length=255, blank=True)
    referral_dump = models.TextField(_("Referral Dump"),null=True,blank=True)
    android_id = models.CharField(_("android_id"), max_length=100, blank=True, null = True, editable = False)

    def __unicode__(self):
        return str(self.code)

class UserPhoneBook(RecordTimeStamp):
    user =  models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), related_name='phonebook',editable=False)
    contact = models.ManyToManyField('forum_user.Contact', verbose_name=_("Contact"),related_name='%(app_label)s_%(class)s_contact')

    def __unicode__(self):
        return self.user

class Contact(RecordTimeStamp):
    contact_name = models.CharField(_("Contact Name"), max_length=100, blank=True, null = True)
    contact_number = models.CharField(_("Contact Number"), max_length=50, blank=True, null = True, db_index = True)
    contact_email = models.CharField(_("Contact Email"), max_length=200, blank=True, null = True)
    is_user_registered = models.BooleanField(default=False)
    user =  models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"),editable=False,null=True,blank=True)
    is_invited = models.BooleanField(default=False)
    invited_on = models.DateTimeField(null=True,blank=True)

    def __unicode__(self):
        return self.contact_name

class DUser(models.Model):
    name = models.CharField(_("Name"), max_length=100, blank=True, null = True)
    gender = models.CharField(choices=gender_option, blank = True, null = True, max_length=10, default='')
    is_used = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name




