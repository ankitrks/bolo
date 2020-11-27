import os
import json
import requests

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from forum.core.conf import settings
from forum.topic.models import RecordTimeStamp
from datetime import datetime
from drf_spirit.utils import language_options
from django.contrib.postgres.fields import ArrayField

class SingUpOTP(models.Model):
    mobile_no = models.CharField(_("title"), max_length=75)
    otp = models.CharField(_("OTP"), max_length=10, editable=False)
    is_active = models.BooleanField(_("Active?"), default=True)
    created_at = models.DateTimeField(_("Created At"), default=timezone.now, blank=True, editable=False)
    used_at = models.DateTimeField(_("Used At"), blank=True, null = True, editable=False)
    is_reset_password = models.BooleanField(_("is reset password?"), default=False)
    is_for_change_phone = models.BooleanField(_("is for change phone number?"), default=False)
    for_user = models.ForeignKey('auth.User', blank = True, null = True)
    api_response_dump = models.TextField(null = True, blank = True)
    
    def __unicode__(self):
        return str(self.mobile_no)

    # def save(self, *args, **kwargs):
    #	if not self.id:
    #		self.otp = generateOTP(6)
    #		response, status = send_sms(self.mobile_no, self.otp)
	#	super(SingUpOTP, self).save(*args, **kwargs)

# # -*- coding: utf-8 -*-

# from __future__ import unicode_literals

# from autoslug import AutoSlugField
# from django.db import models
# from django.db.models import F
# from django.utils.translation import ugettext_lazy as _
# from django.core.urlresolvers import reverse
# from django.conf import settings
# from django.utils import timezone

# from .config import COMMENT_ACTION, COMMENT


# class Category(models.Model):
#     """
#     Category model
#     """
#     parent = models.ForeignKey('self', verbose_name=_("category parent"), blank=True, null=True)

#     title = models.CharField(_("title"), max_length=75)
#     slug = AutoSlugField(populate_from="title", blank=True, unique=True)
#     description = models.CharField(_("description"), max_length=255, blank=True)
#     color = models.CharField(_("color"), max_length=7, blank=True,
#                              help_text=_("Title color in hex format (i.e: #1aafd0)."))

#     is_global = models.BooleanField(_("global"), default=True,
#                                     help_text=_('Designates whether the topics will be'
#                                                 'displayed in the all-categories list.'))
#     is_closed = models.BooleanField(_("closed"), default=False)
#     is_removed = models.BooleanField(_("removed"), default=False)
#     is_private = models.BooleanField(_("private"), default=False)

#     class Meta:
#         ordering = ['-pk']
#         verbose_name = _("category")
#         verbose_name_plural = _("categories")

#     def __unicode__(self):
#         return self.title.encode('utf-8')

#     def get_absolute_url(self):
#         return reverse(
#                 'drf_spirit:category-detail',
#                 kwargs={'pk': str(self.id), 'slug': self.slug})

#     @property
#     def is_subcategory(self):
#         if self.parent_id:
#             return True
#         else:
#             return False


# class Topic(models.Model):
#     """
#     Topic model
#     """
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='spirit_topics', editable=False)
#     category = models.ForeignKey(Category, verbose_name=_("category"))

#     title = models.CharField(_("title"), max_length=255)
#     description = models.TextField(_("description"), default=_("No descriptions"), blank=True)
#     slug = AutoSlugField(populate_from="title", blank=True, unique=True)
#     date = models.DateTimeField(_("date"), default=timezone.now, blank=True, editable=False)
#     last_active = models.DateTimeField(_("last active"), default=timezone.now, blank=True, editable=False)

#     is_pinned = models.BooleanField(_("pinned"), default=False)
#     is_globally_pinned = models.BooleanField(_("globally pinned"), default=False, editable=False)
#     is_closed = models.BooleanField(_("closed"), default=False)
#     is_removed = models.BooleanField(default=False)
#     is_archived = models.BooleanField(default=False)

#     view_count = models.PositiveIntegerField(_("views count"), default=0, editable=False)
#     comment_count = models.PositiveIntegerField(_("comment count"), default=0, editable=False)

#     class Meta:
#         ordering = ['-last_active', '-pk']
#         verbose_name = _("topic")
#         verbose_name_plural = _("topics")

#     def __unicode__(self):
#         return self.title.encode('utf-8')

#     def get_absolute_url(self):
#         return reverse('drf_spirit:topic-detail', kwargs={'pk': str(self.id), 'slug': self.slug})

#     @property
#     def main_category(self):
#         return self.category.parent or self.category

#     def increase_view_count(self):
#         Topic.objects.filter(pk=self.pk).update(view_count=F('view_count') + 1)

#     def increase_comment_count(self):
#         Topic.objects.filter(pk=self.pk).update(comment_count=F('comment_count') + 1, last_active=timezone.now())

#     def decrease_comment_count(self):
#         # todo: update last_active to last() comment
#         Topic.objects.filter(pk=self.pk).update(comment_count=F('comment_count') - 1)


# class Comment(models.Model):

#     user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='forum_comments', editable=False)
#     topic = models.ForeignKey(Topic, related_name='comments')

#     comment = models.TextField(_("comment"))
#     action = models.IntegerField(_("action"), choices=COMMENT_ACTION, default=COMMENT)
#     date = models.DateTimeField(default=timezone.now, blank=True, editable=False)
#     is_removed = models.BooleanField(default=False)
#     is_modified = models.BooleanField(default=False, editable=False)
#     ip_address = models.GenericIPAddressField(blank=True, null=True, editable=False)

#     modified_count = models.PositiveIntegerField(_("modified count"), default=0, editable=False)
#     likes_count = models.PositiveIntegerField(_("likes count"), default=0, editable=False)

#     class Meta:
#         ordering = ['-date', '-pk']
#         verbose_name = _("comment")
#         verbose_name_plural = _("comments")

#     def __unicode__(self):
#         return self.comment[:10].encode('utf-8')

#     def increase_modified_count(self):
#         Comment.objects.filter(pk=self.pk).update(modified_count=F('modified_count') + 1)

#     def increase_likes_count(self):
#         Comment.objects.filter(pk=self.pk).update(likes_count=F('likes_count') + 1)

#     def decrease_likes_count(self):
#         (Comment.objects.filter(pk=self.pk, likes_count__gt=0)
#                         .update(likes_count=F('likes_count') - 1))

#     def save(self, *args, **kwargs):
#         # Comment has pk, means the comment is modified. So increase modified_count and change is_modified
#         if self.pk:
#             self.is_modified = True
#             self.modified_count = F('modified_count') + 1

#         super(Comment, self).save(*args, **kwargs)

#         if self.pk:
#             # comment has pk means modified_count is changed.
#             # As we use F expression, its not possible to know modified_count until refresh from db
#             self.refresh_from_db()

class UserJarvisDump(models.Model):
    DUMP_TYPE = [
        ('1', 'user_activities_data'),
        ('2', 'error_logs'),
        ('3', 'hardware_info'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='User', editable=False, db_index = True, blank = True, null = True)
    dump = models.TextField(_("dump"), null = True, blank = True)
    dump_type = models.CharField(_("dump_type"), choices=DUMP_TYPE, max_length=50, blank=True, null = True)
    sync_time = models.DateTimeField(_("sync_time"), auto_now=False, auto_now_add=True, blank=False, null=False)
    is_executed = models.BooleanField(_("is_executed"), default=False)
    android_id = models.CharField(_("android_id"), max_length=100, blank=True, null = True, editable = False)
    created_at = models.DateTimeField(_("created_at"), auto_now_add = False, auto_now = False, default = datetime.now)
    def __unicode__(self):
        return "%s" % self.dump
      
# code created by akash
# 5 different models for recording user based data
# read the sample dump file and create columns for the same

# class recording the model storing user based statistics 
class UserLogStatistics(models.Model):
    #user_log_fname = os.getcwd() + '/user_log.json'         # file recording the logs of user
    # record these details of the user
    #user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name = 'User', editable = False, max_length = 20)
    user = models.CharField(_("user"), null = True, blank = False, max_length=250, db_index = True)
    user_phone_details = models.CharField(_("phone_details"), null = True, blank = True, max_length=250)
    user_lang = models.CharField(_("user_lang"), null = True, blank = True, max_length=250)
    num_profile_follow = models.TextField(_("num_profile_follow"), null = True, blank = True)
    num_profile_unfollow = models.TextField(_("num_profile_unfollow"), null = True, blank = True)
    num_viewed_profiles = models.TextField(_("num_viewed_profiles"), null = True, blank = True)
    num_profile_reported = models.TextField(_("num_profile_reported"), null = True, blank = True)
    num_viewed_following_list = models.TextField(_("num_viewed_following_list"), null = True, blank = True)
    num_entry_points = models.TextField(_("num_entry_points"), null = True, blank = True)
    num_vb_commented = models.TextField(_("num_vb_commented"), null = True, blank = True)
    num_vb_liked = models.TextField(_("num_vb_liked"), null = True, blank = True)
    num_vb_shared = models.TextField(_("num_vb_shared"), null = True, blank = True)
    num_vb_unliked = models.TextField(_("num_vb_unliked"), null = True, blank = True)
    num_vb_viewed = models.TextField(_("num_vb_viewed"), null = True, blank = True)
    session_starttime = models.DateTimeField(_("session_starttime"), null = True, blank = True)

# class storing the model recroding follow, unfollow, report, share details of a user                  
class UserFollowUnfollowDetails(models.Model):
    # denoting the type of relationshhip applicable here
    relationship_info = [
        ('1', 'follow'),
        ('2', 'unfollow'),
        ('3', 'report'),
        ('4', 'shared'),
    ]

    user = models.CharField(_("user"), null = True, blank = False, max_length = 250, db_index = True)
    profileid = models.TextField(_("profileid"), null = True, blank = True, db_index = True)
    timestamp = models.DateTimeField(_("timestamp"), blank = False, null = False)
    relationship_type = models.CharField(_("relationship_type"), choices = relationship_info, max_length = 50)
    share_medium = models.CharField(_("share_medium"), blank = True, max_length = 300, null = True)
    
# class storing user-videotype details applicable for user, which videos s/he watched, commented, shared etc
class UserVideoTypeDetails(models.Model):
    videoinfo_type = [
        ('1', 'commented'),
        ('2', 'shared'),
        ('3', 'liked'),
        ('4', 'unliked'),
        ('5', 'viewed'),
    ]    
    user = models.CharField(_("user"), null = True, blank = False, max_length = 250, db_index = True)
    videoid = models.CharField(_("videoid"), null = True, blank = True, max_length = 250, db_index = True)
    timestamp = models.DateTimeField(_("timestamp"), null = False, blank = True)
    video_type = models.CharField(_("video_type"), choices = videoinfo_type, max_length = 250)

# class storing video impression details 
class VideoDetails(models.Model):

    # userid has been added a new field
    userid = models.CharField(_("user"), null = True, blank = False, max_length = 250, db_index = True)
    videoid = models.CharField(_("videoid"), null = False, blank = False, max_length = 250, db_index = True)
    timestamp = models.DateTimeField(_("timestamp"), null = True, blank = False)

# class storing user entry point details
class UserEntryPoint(models.Model):

    user = models.CharField(_("user"), null = True, blank = False, max_length = 250, db_index = True)
    entrypoint = models.CharField(_("entrypoint"), null = False, max_length = 400)
    timestamp = models.DateTimeField(_("timestamp"), blank = False, null = False)


# class storing "following" list and "followers" list viewed by a user
class UserViewedFollowersFollowing(models.Model):

    profile_choices = [
        ('1', 'following'),
        ('2', 'followers'),
    ]
    user = models.CharField(_("user"), null = True, blank = False, max_length = 250, db_index = True)
    profileid = models.CharField(_("profileid"), null = False, blank = False, max_length = 250, db_index = True)
    timestamp = models.CharField(_("timestamp"), null = False, blank = True, max_length = 250)
    relationship_type = models.CharField(_("relationship_type"), choices = profile_choices, max_length = 250)

# class storing user category interests 
class UserInterest(models.Model):

    choices = [
        ('1', 'added'),
        ('2', 'removed'),
    ]
    user = models.CharField(_("user"), null = True, blank = False, max_length = 250, db_index = True)
    categoryid = models.CharField(_("categoryid"), null = True, blank = False, max_length = 250, db_index = True)
    timestamp = models.DateTimeField(_("timestamp"), blank = False, null = False)
    category_status = models.CharField(_("category_status"), choices = choices, max_length = 250)

# class storing details of video shared by the user
class VideoSharedDetails(models.Model):

    choices = [
        ('1', 'shared_on_whatsapp'),
        ('2', 'shared_on_fb'),
        ('3', 'shared_on_linkedin'),
        ('4', 'copied_on_clipboard'),
        ('5', 'shared_on_twitter'),
    ]

    user = models.CharField(_("user"), null = True, blank = False, max_length = 250, db_index = True)
    videoid = models.CharField(_("videoid"), null = True, blank = False, max_length = 250, db_index = True)
    share_platform = models.CharField(_("share_platform"), null = True, blank = True, max_length = 400)
    timestamp = models.DateTimeField(_("timestamp"), null = False, blank = False)


# class recording the activity time spend by the user
class ActivityTimeSpend(models.Model):
    user = models.CharField(_("userid"), null = True, blank = False, max_length = 250, db_index = True)
    fragmentid = models.CharField(_("fragmentid"), null = True, blank = False, max_length = 550, db_index = True)
    time_spent = models.PositiveIntegerField(_("time_spent(ms)"), default = 0, editable = False)
    timestamp = models.DateTimeField(_("timestamp"), null = True, blank = False)
    
# class recording the seach records of a user
class UserSearch(models.Model):
    user = models.CharField(_("user"), null = True, blank = False, max_length = 250, db_index = True)
    searchquery = models.CharField(_("searchquery"), null = True, blank = False, max_length = 1000)
    timestamp = models.DateTimeField(_("timestamp"), null = True, blank = False)


# class recording the user --> datetime mapping
class UserTimeRecord(models.Model):
    user = models.CharField(_("user"), null = True, blank = True, max_length = 250, db_index = True)
    timestamp = models.DateTimeField(_("timestamp"), null = True, blank = False)

# class recording the day, hour, month, year --> frequency mapping
class HourlyActiveUser(models.Model):
    day_month = models.CharField(_("day_month"), null = True, blank = False, max_length = 250)
    day_week = models.CharField(_("day_week"), null = True, blank = False, max_length = 250)
    hour = models.CharField(_("hour"), null = True, blank = False, max_length = 250)
    month = models.CharField(_("month"), null = True, blank = False, max_length = 250)
    year = models.PositiveIntegerField(_("year"), default = 2019, editable = False)
    frequency = models.PositiveIntegerField(_("frequency"), default=0, editable=False)
    date_time_field = models.DateTimeField(_("date_time_field"), null = True, blank = False)

# class recording the day --> frequency mapping
class DailyActiveUser(models.Model):
    day_month_year = models.CharField(_("day_month_year"), null = True, blank = False, max_length = 250)
    frequency = models.PositiveIntegerField(_("frequency"), default = 0, editable = False)
    date_time_field = models.DateTimeField(_("date_time_field"), null = True, blank = False)

# class recording the month, year --> frequency
class MonthlyActiveUser(models.Model):    
    month = models.CharField(_("month"), null = True, blank = False, max_length = 250)
    year = models.PositiveIntegerField(_("year"), default = 2019, editable = False)
    frequency = models.PositiveIntegerField(_("frequency"), default = 0, editable = False)

# class recording the hardware data corrosponding the logs
class HardwareData(models.Model):
    user_id = models.CharField(_("userid"), null = True, blank = True, max_length = 250, db_index = True)
    total_memory = models.PositiveIntegerField(_("total_memory"), default = 0., editable = False)
    memory_free = models.PositiveIntegerField(_("memory_free"), default = 0, editable = False)
    memory_available = models.PositiveIntegerField(_("memory_available"), default = 0, editable = False)
    swap_cached = models.PositiveIntegerField(_("swap_cached"), default = 0, editable = False)
    active = models.PositiveIntegerField(_("active"), default = 0, editable = False)
    inactive = models.PositiveIntegerField(_("inactive"), default = 0, editable = False)
    unevictable = models.PositiveIntegerField(_("unevictable"), default = 0, editable = False)
    locked = models.PositiveIntegerField(_("locked"), default = 0, editable = False)
    swap_total = models.PositiveIntegerField(_("swap_total"), default = 0, editable = False)
    swap_free = models.PositiveIntegerField(_("swap_free"), default = 0, editable = False)
    dirty = models.PositiveIntegerField(_("dirty"), default = 0, editable = False)
    write_back = models.PositiveIntegerField(_("write_back"), default = 0, editable = False)
    annon_pages = models.PositiveIntegerField(_("annon_pages"), default = 0, editable = False)
    mapped = models.PositiveIntegerField(_("mapped"), default = 0, editable = False)
    shmem = models.PositiveIntegerField(_("shmem"), default = 0, editable = False)
    slab = models.PositiveIntegerField(_("slab"), default = 0, editable = False)
    sreclaimable = models.PositiveIntegerField(_("sreclaimable"), default = 0, editable = False)
    sunreclaimable = models.PositiveIntegerField(_("sunreclaimable"), default = 0, editable = False)
    kernelstack = models.PositiveIntegerField(_("kernelstack"), default = 0, editable = False)
    pagetables = models.PositiveIntegerField(_("pagetables"), default = 0, editable = False)
    nfs_unstable = models.PositiveIntegerField(_("nfs_unstable"), default = 0, editable = False)
    bounce = models.PositiveIntegerField(_("bounce"), default = 0, editable = False)
    writebacktemp = models.PositiveIntegerField(_("writebacktemp"), default = 0, editable = False)
    commit_limit = models.PositiveIntegerField(_("commit_limit"), default = 0, editable = False)
    commit_as = models.PositiveIntegerField(_("commit_as"), default = 0, editable = False)
    malloc_total = models.PositiveIntegerField(_("malloc_total"), default = 0, editable = False)
    malloc_used = models.PositiveIntegerField(_("malloc_used"), default = 0, editable = False)
    malloc_chunk = models.PositiveIntegerField(_("malloc_chunk"), default = 0, editable = False)

# class related to user feedback
class UserFeedback(models.Model):
    by_user = models.ForeignKey('auth.User', blank = True, null = True, editable = False)
    created_at = models.DateTimeField(auto_now=False,auto_now_add=True,blank=False,null=False)
    contact_email = models.CharField(_("contact_email"), max_length=30)
    contact_number = models.CharField(_("contact_number"), max_length=30, default='')
    description = models.TextField(null = True, blank = True)
    feedback_image = models.CharField(_("feedback_image"), max_length=255)

    def send_feedback_email(self):
        try:
            content_email = """
                Hello, <br><br>
                We have received a feedback from %s. Please find the details below:<br><br>
                <b>Name:</b> %s <br>
                <b>Feedback:</b> %s <br>
                <b>Contact Email:</b> %s <br>
                <b>Contact Number:</b> %s <br>
                <b>Image:</b><br>
                <img src="%s"> <br><br>
                Thanks,<br>
                Team BoloIndya
                """ %(self.user_name(), self.user_name(), self.description, \
                        self.contact_email, self.contact_number, self.feedback_image)
            requests.post(
                "https://api.mailgun.net/v3/mail.careeranna.com/messages",
                auth=("api", "d6c66f5dd85b4451bbcbd94cb7406f92-bbbc8336-97426998"),
                data={"from": "BoloIndya Support <support@boloindya.com>",
                      "to": ["support@boloindya.com"],
                      "cc":[self.contact_email],
                      "bcc":["anshika@careeranna.com", "gitesh@careeranna.com"],
                      "subject": "BoloIndya Feedback Received | " + self.user_name() + ' | ' + self.user_contact(),
                      "html": content_email
                }
            )
        except:
            pass
        return True

    def user_contact(self):
        try:
            if self.by_user and self.by_user.st and self.by_user.st.mobile_no:
                return self.by_user.st.mobile_no
            else:
                return self.contact_email
        except Exception as e:
            print e
            return self.contact_email

    def user_name(self):
        try:
            if self.by_user and self.by_user.st and self.by_user.st.name:
                return self.by_user.st.name
            else:
                return self.by_user.username
        except Exception as e:
            print e
            return self.by_user.username

class Campaign(RecordTimeStamp):
    banner_img_url = models.TextField(_("Banner Image URL"), blank = False, null = False)
    details = models.TextField(_("Campaign Details"), blank = True, null = True)
    show_popup_on_app = models.BooleanField(default=False)
    popup_img_url = models.TextField(_("Popup Image URL"), blank = True, null = True)
    hashtag = models.ForeignKey('forum_topic.TongueTwister', verbose_name=_("HashTag"), related_name="campaign_hashtag",null=False,blank=False)
    is_active = models.BooleanField(default=True)
    active_from = models.DateTimeField(_("Active From"), auto_now=False, blank=False, null=False)
    active_till = models.DateTimeField(_("Active Till"), auto_now=False, blank=False, null=False)
    is_winner_declared = models.BooleanField(default=False)
    winners = models.ManyToManyField('Winner', verbose_name=_("winner"), \
            related_name="m2mwinner_campaign",blank=True)
    next_campaign_hashtag = models.ForeignKey('forum_topic.TongueTwister', verbose_name=_("NextCampaignHashTag"), related_name="campaign_next_hashtag",null=True,blank=True)
    languages = ArrayField(models.CharField(max_length=200), blank=True, default=list('0'))

class Winner(RecordTimeStamp):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank = False, null = False, related_name='winner_user')
    rank = models.PositiveSmallIntegerField(_("Rank"), blank=False, null=False)
    extra_text = models.TextField(_("Extra Text"), blank = True, null = True)
    video = models.ForeignKey('forum_topic.Topic', verbose_name=_("Video"), related_name="winner_video",null=False,blank=False)

    def __unicode__(self):
       return str(self.rank) +': '+ self.user.st.name

class Country(RecordTimeStamp):
    name = models.CharField(_("country_name"), max_length=100, null=True, blank=True)
    place_id = models.CharField(_("country_place_id"), max_length=350, null=True, blank=True)
    def __unicode__(self):
       return str(self.name)

class State(RecordTimeStamp):
    name = models.CharField(_("state_name"), max_length=100, null=True, blank=True)
    place_id = models.CharField(_("state_place_id"), max_length=350, null=True, blank=True)
    country = models.ForeignKey(Country, blank = True, null = True, related_name='state_country')
    def __unicode__(self):
       return str(self.name)+', '+str(self.country)

class City(RecordTimeStamp):
    name = models.CharField(_("city_name"), max_length=100, null=True, blank=True)
    place_id = models.CharField(_("city_place_id"), max_length=350, null=True, blank=True)
    state = models.ForeignKey(State, blank = True, null = True, related_name='city_state')
    def __unicode__(self):
       return str(self.name)+', '+str(self.state)

class MusicAlbum(models.Model):
    title = models.CharField(_("title"),null=True,blank=True,max_length=1000)
    s3_file_path = models.CharField(_("s3 file path"),null=True,blank=True,max_length=1000)
    image_path = models.CharField(_("image path"),null=True,blank=True,max_length=1000)
    author_name = models.CharField(_("author name"),null=True,blank=True,max_length=1000)
    language_id = models.CharField(_("language"), choices=language_options, blank = True, null = True, max_length=10, default='1')
    order_no = models.PositiveIntegerField(_("order_no"), default = 0)
    last_modified = models.DateTimeField(_("last_modified"),auto_now=True, auto_now_add=False,blank=False, null=False)
    def __unicode__(self):
       return str(self.title)+', '+str(self.author_name)
    class Meta:
        ordering = ['order_no']


class SystemParameter(models.Model):
    name = models.CharField(max_length=200)
    value = models.TextField()

    def __unicode__(self):
        return '%s = %s'%(self.name, self.value)


class DatabaseRecordCount(models.Model):
    name = models.CharField(max_length=200)
    query = models.TextField()
    count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(_('Last Updated'), auto_now=True, auto_now_add=False)
    update_time = models.PositiveIntegerField(_('Update Time'), default=60)

    def __unicode__(self):
        return '%s = %s'%(self.name, self.count)

    @staticmethod
    def get_value(name):
        return DatabaseRecordCount.objects.get(name=name).count