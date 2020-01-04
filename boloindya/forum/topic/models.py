# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import urllib2
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.db.models import F

from .managers import TopicQuerySet
from ..core.utils.models import AutoSlugField
from ..core.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from fcm.models import AbstractDevice
from django.db.models import F,Q
from drf_spirit.utils import reduce_bolo_score, shortnaturaltime, add_bolo_score,language_options
from forum.user.models import UserProfile, Weight
from django.http import JsonResponse
from datetime import datetime,timedelta

from .transcoder import transcode_media_file
from django.utils.html import format_html


class RecordTimeStamp(models.Model):
    created_at=models.DateTimeField(auto_now=False,auto_now_add=True,blank=False,null=False) # auto_now will add the current time and date whenever field is saved.
    last_modified=models.DateTimeField(auto_now=True,auto_now_add=False)                     # while auto_now_add will save the date and time only when record is first created
    class Meta:
        abstract = True

class UserInfo(RecordTimeStamp):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, related_name='%(app_label)s_%(class)s_user',editable=False)
    is_active = models.BooleanField(default = True)

    def get_user(self):
        if self.user is not None and self.user.userprofile is not None:
            return '%s' %(self.user.userprofile.name)
        return None
    class Meta:
        abstract = True

class BoloActionHistory(RecordTimeStamp):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False)
    score = models.PositiveIntegerField(_("Bolo Score"), default=0)
    action = models.ForeignKey(Weight, editable=False)
    action_object_type = models.ForeignKey(ContentType, verbose_name=('topic type'),null=True,blank=True)
    action_object_id = models.PositiveIntegerField(('object ID'),null=True,blank=True)
    action_object = GenericForeignKey('action_object_type', 'action_object_id')
    is_removed = models.BooleanField(default=False)
    is_encashed = models.BooleanField(default=False)
    is_eligible_for_encash = models.BooleanField(default=True)
    enchashable_detail = models.ForeignKey('forum_payment.EncashableDetail',null=True,blank=True,related_name='bolo_score_items',editable=False)
    
    def __unicode__(self):
        return self.user.username

    def name(self):
        from django.utils.html import format_html
        if self.user.st.name:
            return format_html('<a href="/superman/forum_user/userprofile/' + str(self.user.st.id) \
                + '/change/" target="_blank">' + self.user.st.name + '</a>' )
        return format_html('<a href="/superman/forum_user/userprofile/' + str(self.user.st.id) \
            + '/change/" target="_blank">' + self.user.username + '</a>' )

class Topic(models.Model):
    """
    Topic model

    :ivar last_active: Last time a comment was added/removed,\
    it makes the search re-index the topic
    :vartype last_active: `:py:class:models.DateTimeField`
    :ivar reindex_at: Last time this model was marked\
    for reindex. It makes the search re-index the topic,\
    it must be set explicitly
    :vartype reindex_at: `:py:class:models.DateTimeField`
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='st_topics')
    category = models.ForeignKey('forum_category.Category', verbose_name=_("category"), related_name="category_topics",null=True,blank=True)
    m2mcategory = models.ManyToManyField('forum_category.Category', verbose_name=_("category"), \
            related_name="m2mcategories_topics",blank=True)
    hash_tags = models.ManyToManyField('forum_topic.TongueTwister', verbose_name=_("hash_tags"), \
            related_name="hash_tag_topics",blank=True)

    title = models.TextField(_("title"), blank = True, null = True)
    question_audio = models.CharField(_("audio title"), max_length=255, blank = True, null = True)
    question_video = models.CharField(_("video title"), max_length=255, blank = True, null = True)
    slug = AutoSlugField(populate_from="title", db_index=False, blank=True)
    date = models.DateTimeField(_("date"), default=timezone.now)
    last_active = models.DateTimeField(_("last active"), default=timezone.now)
    reindex_at = models.DateTimeField(_("reindex at"), default=timezone.now)
    language_id = models.CharField(_("language"), choices=language_options, blank = True, null = True, max_length=10, default='1')
    question_image = models.TextField(_("Question image"),null=True,blank=True)
    is_popular = models.BooleanField(_("Popular"), default = False)
    is_pubsub_popular_push = models.BooleanField(_("Popular Push"), default = False)

    is_media = models.BooleanField(default=True)
    media_duration = models.CharField(_("duration"), max_length=20, default='',null=True,blank=True)
    last_commented = models.DateTimeField(_("Last Commented"),null=True,blank=True, default=timezone.now)

    is_pinned = models.BooleanField(_("pinned"), default=False)
    is_globally_pinned = models.BooleanField(_("globally pinned"), default=False)
    is_closed = models.BooleanField(_("closed"), default=False)
    is_removed = models.BooleanField(_("removed"), default=False)
    thumbnail = models.CharField(_("thumbnail"), max_length=150, blank = True, null = True, default='')
    view_count = models.PositiveIntegerField(_("views"), default=0)
    comment_count = models.PositiveIntegerField(_("comment count"), default=0)
    total_share_count = models.PositiveIntegerField(_("Total Share count"), default=0)# self plus comment
    share_count = models.PositiveIntegerField(_("Share count"), default=0)# only topic share
    # share_user = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True, related_name='share_topic_user')
    # shared_post = models.ForeignKey('self', blank = True, null = True, related_name='user_shared_post')
    is_vb = models.BooleanField(_("Is Video Bytes"), default=False)
    likes_count = models.PositiveIntegerField(_("Likes count"), default=0)

    is_monetized = models.BooleanField(_("monetized"), default=False)
    vb_width = models.PositiveIntegerField(_("vb width"), default=0)
    vb_height = models.PositiveIntegerField(_("vb height"), default=0)

    whatsapp_share_count = models.PositiveIntegerField(null=True,blank=True,default=0)
    linkedin_share_count = models.PositiveIntegerField(null=True,blank=True,default=0)
    facebook_share_count = models.PositiveIntegerField(null=True,blank=True,default=0)
    twitter_share_count = models.PositiveIntegerField(null=True,blank=True,default=0)

    backup_url = models.TextField(_("backup url"), blank = True)
    is_transcoded = models.BooleanField(default = False)
    is_transcoded_error = models.BooleanField(default = False)
    transcode_job_id = models.TextField(_("Transcode Job ID"), blank = True)
    transcode_dump = models.TextField(_("Transcode Dump"), blank = True)
    transcode_status_dump = models.TextField(_("Transcode Status Dump (Job Status)"), blank = True)

    m3u8_content = models.TextField(_("M3U8 Content"), blank = True, null = True)
    audio_m3u8_content = models.TextField(_("Audio M3U8 Content"), blank = True, null = True)
    video_m3u8_content = models.TextField(_("Video M3U8 Content"), blank = True, null = True)

    objects = TopicQuerySet.as_manager()

    def __unicode__(self):
        return self.title

    def has_answers(self):
        return self.topic_comment.all().count()
    def get_video_comments(self):
        return self.topic_comment.filter(is_media = True, is_audio = False)
    def get_audio_comments(self):
        return self.topic_comment.filter(is_media = True, is_audio = True)
    def get_text_comments(self):
        return self.topic_comment.filter(is_media = False)

    class Meta:
        ordering = ['-comment_count', '-total_share_count']
        verbose_name = _("topic")
        verbose_name_plural = _("topics")

    def update_m3u8_content(self):
        try:
            if self.question_video:
                m3u8_url = self.question_video
                url_split = m3u8_url.split('/')
                audio_url = '/'.join( url_split[:-1] + ['hlsAudio'] + [url_split[-1].replace('hls_', '')] )
                video_url = '/'.join( url_split[:-1] + ['hls1000k'] + [url_split[-1].replace('hls_', '')] )

                self.m3u8_content = urllib2.urlopen(m3u8_url).read()
                self.audio_m3u8_content = urllib2.urlopen(audio_url).read()
                self.video_m3u8_content = urllib2.urlopen(video_url).read()
                self.save()
        except:
            pass

    def update_vb(self, *args, **kwargs):
        if not self.id or not self.is_transcoded:
            if self.is_vb and self.question_video:
                data_dump, m3u8_url, job_id = transcode_media_file(self.question_video.split('s3.amazonaws.com/')[1])
                if m3u8_url:
                    self.backup_url = self.question_video
                    self.question_video = m3u8_url
                    self.transcode_dump = data_dump
                    self.transcode_job_id = job_id
                    # self.is_transcoded = True
                    self.save()
                    self.update_m3u8_content()
    
    def watermark_vb(self, *args, **kwargs):
        data_dump, m3u8_url, job_id = transcode_media_file(self.question_video.split('s3.amazonaws.com/')[1])
        # print m3u8_url,"====>",job_id
        if m3u8_url:
            self.backup_url = self.question_video
            self.question_video = m3u8_url
            self.transcode_dump = data_dump
            self.transcode_job_id = job_id
            self.is_transcoded = True
        self.save()

    def get_absolute_url(self):
        if self.category_id == settings.ST_TOPIC_PRIVATE_CATEGORY_PK:
            return reverse('spirit:topic:private:detail', kwargs={'topic_id': str(self.id), 'slug': self.slug})
        else:
            return reverse('spirit:topic:detail', kwargs={'pk': str(self.id), 'slug': self.slug})

    def get_bookmark_url(self):
        if not self.is_visited:
            return self.get_absolute_url()

        if not self.has_new_comments:
            return self.bookmark.get_absolute_url()

        return self.bookmark.get_new_comment_url()

    @property
    def main_category(self):
        return self.category.parent or self.category

    @property
    def bookmark(self):
        # *bookmarks* is dynamically created by manager.with_bookmarks()
        try:
            assert len(self.bookmarks) <= 1, "Panic, too many bookmarks"
            return self.bookmarks[0]
        except (AttributeError, IndexError):
            return

    @property
    def new_comments_count(self):
        # This may not be accurate since bookmarks requires JS,
        # without JS only the first comment in a page is marked,
        # so this counter should be shown running a JS script
        if not self.bookmark:
            return 0

        # Comments may have been moved
        return max(0, self.comment_count - self.bookmarks[0].comment_number)

    @property
    def has_new_comments(self):
        return self.new_comments_count > 0

    @property
    def is_visited(self):
        return bool(self.bookmark)

    def increase_view_count(self):
        Topic.objects\
            .filter(pk=self.pk)\
            .update(view_count=F('view_count') + 1)
        UserProfile.objects\
            .filter(user_id=self.user.id)\
            .update(view_count=F('view_count') + 1)

    def increase_comment_count(self):
        Topic.objects\
            .filter(pk=self.pk)\
            .update(comment_count=F('comment_count') + 1, last_active=timezone.now())

    def decrease_comment_count(self):
        # todo: update last_active to last() comment
        Topic.objects\
            .filter(pk=self.pk)\
            .update(comment_count=F('comment_count') - 1)

    def get_all_comments_html(self):
        """
        For search indexing

        :return: List of comments in HTML
        """
        return self.comment_set.values_list('comment_html', flat=True)

    def name(self):
        from django.utils.html import format_html
        if self.user.st.name:
            return format_html('<a href="/superman/forum_user/userprofile/' + str(self.user.st.id) \
                + '/change/" target="_blank">' + self.user.st.name + '</a>' )
        return format_html('<a href="/superman/forum_user/userprofile/' + str(self.user.st.id) \
            + '/change/" target="_blank">' + self.user.username + '</a>' )

    def delete(self):
        if self.is_monetized:
            if self.language_id == '1':
                reduce_bolo_score(self.user.id, 'create_topic_en', self, 'deleted')
            else:
                reduce_bolo_score(self.user.id, 'create_topic', self, 'deleted')
        else:
            notify_owner = Notification.objects.create(for_user_id = self.user.id ,topic = self, \
                notification_type='7', user_id = self.user.id)
        self.is_monetized = False
        self.is_removed = True
        self.save()
        userprofile = UserProfile.objects.get(user = self.user)
        if userprofile.vb_count and self.is_vb:
            userprofile.vb_count = F('vb_count')-1
        userprofile.save()
        return True

    def restore(self):
        self.is_removed = False
        self.save()
        userprofile = UserProfile.objects.get(user = self.user)
        if self.is_vb: # userprofile.vb_count
            userprofile.vb_count = F('vb_count')+1
        userprofile.save()
        # Bolo actions will be added only when the monetization is enabled
        # add_bolo_score(self.user.id, 'create_topic', self)
        return True

    def no_monetization(self):
        if self.is_monetized:
            self.is_monetized = False
            self.save()
            userprofile = UserProfile.objects.get(user = self.user)
            userprofile.save()
            if self.language_id == '1':
                reduce_bolo_score(self.user.id, 'create_topic_en', self, 'no_monetize')
            else:
                reduce_bolo_score(self.user.id, 'create_topic', self, 'no_monetize')
            return True
        else:
            return True

    def add_monetization(self):
        self.is_removed = False
        self.is_monetized = True
        self.save()
        userprofile = UserProfile.objects.get(user = self.user)
        userprofile.save()
        if self.language_id =='1':
            add_bolo_score(self.user.id, 'create_topic_en', self)
        else:
            add_bolo_score(self.user.id, 'create_topic', self)
        return True

    def audio_duration(self):
        all_audio_answer = self.topic_comment.filter(is_media=True,is_audio = True)
        duration =datetime.strptime('00:00', '%M:%S')
        for each_audio in all_audio_answer:
            # print each_audio.media_duration,"maaz"
            if each_audio.media_duration and not each_audio.media_duration =='00:00':
                # print each_audio.media_duration,'a'
                datetime_object = datetime.strptime(each_audio.media_duration, '%M:%S')
                a = timedelta(minutes=datetime_object.minute, seconds=datetime_object.second)
                # b = timedelta(minutes=duration.minute, seconds=duration.second)
                # print a,duration
                duration=a+duration
                # print duration, type(duration)
                # duration = timedelta(hours = b.hour,minutes=b.minute, seconds=b.second)
            else:
                pass
        duration = str(duration.hour)+":"+str(duration.minute)+":"+str(duration.second)
        return duration

    def video_duration(self):
        all_audio_answer = self.topic_comment.filter(is_media=True,is_audio = False)
        duration =datetime.strptime('00:00', '%M:%S')
        for each_audio in all_audio_answer:
            # print each_audio.media_duration,"maaz"
            if each_audio.media_duration and not each_audio.media_duration =='00:00':
                # print each_audio.media_duration,'a'
                datetime_object = datetime.strptime(each_audio.media_duration, '%M:%S')
                a = timedelta(minutes=datetime_object.minute, seconds=datetime_object.second)
                # b = timedelta(minutes=duration.minute, seconds=duration.second)
                # print a,duration
                duration=a+duration
                # print duration, type(duration)
                # duration = timedelta(hours = b.hour,minutes=b.minute, seconds=b.second)
            else:
                pass
        duration = str(duration.hour)+":"+str(duration.minute)+":"+str(duration.second)
        return duration

    def duration(self):
        if self.media_duration:
            return format_html('<a href="' + self.backup_url + '" target="_blank">' + self.media_duration + '</a>' )
        return "00:00"

    def comments(self):
        if self.comment_count:
            return format_html(str('<a href="/superman/forum_comment/comment/?topic_id='+str(self.id)+'" target="_blank">' \
                + str(self.comment_count)+'</a>'))
        return 0

class TopicHistory(RecordTimeStamp):
    source = models.ForeignKey('forum_topic.Topic', blank = False, null = False, related_name='topic_history')
    hash_tags = models.ManyToManyField('forum_topic.TongueTwister', verbose_name=_("hash_tags"), \
            related_name="hash_tag_topics_history",blank=True)
    title = models.TextField(_("title"), blank = True, null = True)

    def __unicode__(self):
        return str(self.title)


class VBseen(UserInfo):
    topic = models.ForeignKey(Topic, related_name='vb_seen',null=True,blank=True)
    def __unicode__(self):
        return unicode(str(self.topic if self.topic else 'VB'), 'utf-8')

class TongueTwister(models.Model):
    hash_tag = models.CharField(_("Hash Tag"), max_length=255, blank = True, null = True)
    en_descpription = models.TextField(_("English Hash Tag Description"),blank = True, null = True)
    hi_descpription = models.TextField(_("Hindi Hash Tag Description"),blank = True, null = True)
    ta_descpription = models.TextField(_("Tamil Hash Tag Description"),blank = True, null = True)
    te_descpription = models.TextField(_("Telgu Hash Tag Description"),blank = True, null = True)
    be_descpription = models.TextField(_("Bengali Hash Tag Description"),blank = True, null = True)
    ka_descpription = models.TextField(_("Kannada Hash Tag Description"),blank = True, null = True)
    ma_descpription = models.TextField(_("Malyalam Hash Tag Description"),blank = True, null = True)
    gj_descpription = models.TextField(_("Gujrati Hash Tag Description"),blank = True, null = True)
    mt_descpription = models.TextField(_("Marathi Hash Tag Description"),blank = True, null = True)
    picture = models.CharField(_("Picture URL"),max_length=255, blank=True,null=True)
    hash_counter = models.PositiveIntegerField(default=1,null=True,blank=True)
    total_views = models.PositiveIntegerField(default=0,null=True,blank=True)
    def __unicode__(self):
        return str(self.hash_tag)

class ShareTopic(UserInfo):
    topic = models.ForeignKey(Topic, related_name='share_topic_topic_share',null=True,blank=True)
    comment = models.ForeignKey('forum_comment.Comment',related_name='share_topic_topic_comment',null=True,blank=True)

    def __unicode__(self):
        return str(self.topic if self.topic else self.comment)

class Like(UserInfo):
    comment = models.ForeignKey('forum_comment.Comment',related_name='like_topic_comment',null=True,blank=True)
    topic = models.ForeignKey(Topic, related_name='like_topic_share',null=True,blank=True)
    like = models.BooleanField(default = True)

    def __unicode__(self):
        return str(self.topic if self.topic else self.comment)

share_type_options = (
    ('0', "facebook"),
    ('1', "whatsapp"),
    ('2', "linkedin"),
    ('2', "twitter"),
)
class SocialShare(UserInfo):
    share_type = models.CharField(choices=share_type_options, blank = True, null = True, max_length=10)
    topic = models.ForeignKey(Topic, related_name='social_share_topic_share',null=True,blank=True)
    comment = models.ForeignKey('forum_comment.Comment',related_name='social_share_topic_comment',null=True,blank=True)
    def __unicode__(self):
        return str(self.share_type)

class Notification(UserInfo):
    for_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,blank=True,editable=False)
    # device_id = models.CharField(_("Device Id"), max_length=255, blank = True, null = True)
    notification_type = models.CharField(_("notification_type"), max_length=5, default='1')
    is_read = models.BooleanField(default=False)
    status = models.PositiveIntegerField(default=0)# 0=new, 1=pushed, 2=read
    read_at = models.DateTimeField(null=True,blank=True)
    topic_type = models.ForeignKey(ContentType, verbose_name=('topic type'),null=True,blank=True)
    topic_id = models.PositiveIntegerField(('object ID'),null=True,blank=True)
    topic = GenericForeignKey('topic_type', 'topic_id')

    def __unicode__(self):
        return str(self.topic)

    def get_notification_json(self):
        notific ={}
        if self.notification_type=='1':
            notific['title'] = str(self.user.st.name)+' has posted a video: '+self.topic.title+'. Would you like to comment?'
            notific['hindi_title'] = str(self.user.st.name)+' ने एक वीडियो पोस्ट किया है: '+self.topic.title+'. क्या आप टिपण्णी करना चाहेंगे?'
            notific['tamil_title'] = str(self.user.st.name)+' ஒரு வீடியோவை வெளியிட்டுள்ளது: '+self.topic.title+' நீங்கள் கருத்து தெரிவிக்க விரும்புகிறீர்களா?'
            notific['telgu_title'] = str(self.user.st.name)+' ఒక వీడియోను పోస్ట్ చేసింది: '+self.topic.title+'. మీరు వ్యాఖ్యానించాలనుకుంటున్నారా?'
            notific['bengali_title'] = str(self.user.st.name)+' একটি ভিডিও পোস্ট করেছে: '+self.topic.title+'. আপনি মন্তব্য করতে চান?'
            notific['kannada_title'] = str(self.user.st.name)+' ವೀಡಿಯೊವನ್ನು ಪೋಸ್ಟ್ ಮಾಡಿದೆ: '+self.topic.title+'. ನೀವು ಕಾಮೆಂಟ್ ಮಾಡಲು ಬಯಸುವಿರಾ?'
            notific['malayalam_title'] = str(self.user.st.name)+' ഒരു വീഡിയോ പോസ്റ്റുചെയ്‌തു: '+self.topic.title+'. അഭിപ്രായമിടാൻ നിങ്ങൾ ആഗ്രഹിക്കുന്നുണ്ടോ?'
            notific['gujrati_title'] = str(self.user.st.name)+' વિડિઓ પોસ્ટ કરી છે: '+self.topic.title+'. તમે ટિપ્પણી કરવા માંગો છો?'
            notific['marathi_title'] = str(self.user.st.name)+' एक व्हिडिओ पोस्ट केला आहे: '+self.topic.title+'. आपण टिप्पणी देऊ इच्छिता?'
            
            notific['notification_type'] = '1'
            notific['instance_id'] = self.topic.id
            notific['read_status'] = self.status
            notific['id'] = self.id
            notific['created_at'] = shortnaturaltime(self.created_at)
            notific['actor_profile_pic'] = self.user.st.profile_pic

        elif self.notification_type=='2':
            notific['title'] = str(self.user.st.name)+' has commented on video: '+self.topic.topic.title+'.'
            notific['hindi_title'] = str(self.user.st.name)+' ने वीडियो पर टिप्पणी की है: '+self.topic.topic.title
            notific['tamil_title'] = str(self.user.st.name)+' வீடியோவில் கருத்து தெரிவித்துள்ளது: '+self.topic.topic.title
            notific['telgu_title'] = str(self.user.st.name)+' వీడియోపై వ్యాఖ్యానించారు: '+self.topic.topic.title
            notific['bengali_title'] = str(self.user.st.name)+' ভিডিওতে মন্তব্য করেছে: '+self.topic.topic.title+'.'
            notific['kannada_title'] = str(self.user.st.name)+' ವೀಡಿಯೊದಲ್ಲಿ ಕಾಮೆಂಟ್ ಮಾಡಿದ್ದಾರೆ: '+self.topic.topic.title+'.'
            notific['malayalam_title'] = str(self.user.st.name)+' വീഡിയോയിൽ അഭിപ്രായമിട്ടു: '+self.topic.topic.title+'.'
            notific['gujrati_title'] = str(self.user.st.name)+' વિડિઓ પર ટિપ્પણી કરી છે: '+self.topic.topic.title+'.'
            notific['marathi_title'] = str(self.user.st.name)+' व्हिडिओवर टिप्पणी दिली आहे: '+self.topic.topic.title+'.'
            
            notific['notification_type'] = '2'
            notific['instance_id'] = self.topic.id
            notific['topic_id'] = self.topic.topic.id
            notific['read_status'] = self.status
            notific['id'] = self.id
            notific['created_at'] = shortnaturaltime(self.created_at)
            notific['actor_profile_pic'] = self.user.st.profile_pic 

        elif self.notification_type=='3':
            notific['title'] = str(self.user.st.name)+' has commented on your video: '+self.topic.topic.title
            notific['hindi_title'] = str(self.user.st.name)+' ने आपके वीडियो पर टिप्पणी की है: '+self.topic.topic.title
            notific['tamil_title'] = str(self.user.st.name)+' உங்கள் வீடியோவில் கருத்து தெரிவித்துள்ளது: '+self.topic.topic.title
            notific['telgu_title'] = str(self.user.st.name)+' మీ వీడియోపై వ్యాఖ్యానించారు: '+self.topic.topic.title
            notific['bengali_title'] = str(self.user.st.name)+' আপনার ভিডিওতে মন্তব্য করেছে: '+self.topic.topic.title
            notific['kannada_title'] = str(self.user.st.name)+' ನಿಮ್ಮ ವೀಡಿಯೊದಲ್ಲಿ ಕಾಮೆಂಟ್ ಮಾಡಿದ್ದಾರೆ: '+self.topic.topic.title
            notific['malayalam_title'] = str(self.user.st.name)+' നിങ്ങളുടെ വീഡിയോയിൽ അഭിപ്രായമിട്ടു: '+self.topic.topic.title
            notific['gujrati_title'] = str(self.user.st.name)+' તમારી વિડિઓ પર ટિપ્પણી કરી છે: '+self.topic.topic.title
            notific['marathi_title'] = str(self.user.st.name)+' आपल्या व्हिडिओवर टिप्पणी दिली आहे: '+self.topic.topic.title
            notific['notification_type'] = '3'
            notific['instance_id'] = self.topic.id
            notific['topic_id'] = self.topic.topic.id
            notific['read_status'] = self.status
            notific['id'] = self.id
            notific['created_at'] = shortnaturaltime(self.created_at)
            notific['actor_profile_pic'] = self.user.st.profile_pic 

        elif self.notification_type=='4':
            notific['title'] = str(self.user.st.name)+' followed you'
            notific['hindi_title'] = str(self.user.st.name)+' ने आपको फॉलो किया'
            notific['tamil_title'] = str(self.user.st.name)+' பாலோ செய்துள்ளார்'
            notific['telgu_title'] = str(self.user.st.name)+' మీరు అనుసరించారు'
            notific['bengali_title'] = str(self.user.st.name)+' তোমাকে অনুসরণ করেছিল'
            notific['kannada_title'] = str(self.user.st.name)+' ನಿಮ್ಮನ್ನು ಹಿಂಬಾಲಿಸಿದರು'
            notific['malayalam_title'] = str(self.user.st.name)+' നിങ്ങളെ പിന്തുടർന്നു'
            notific['gujrati_title'] = str(self.user.st.name)+' તમારી પાછળ'
            notific['marathi_title'] = str(self.user.st.name)+' आपण अनुसरण'
            notific['notification_type'] = '4'
            notific['instance_id'] = self.user.id
            notific['read_status'] = self.status
            notific['id'] = self.id
            notific['created_at'] = shortnaturaltime(self.created_at)
            notific['actor_profile_pic'] = self.user.st.profile_pic 

        elif self.notification_type=='5':
            notific['title'] = str(self.user.st.name)+' liked your video'
            notific['hindi_title'] = str(self.user.st.name)+' को आपका वीडियो पसंद आया'
            notific['tamil_title'] = str(self.user.st.name)+' உங்கள் வீடியோவை விரும்பியது'
            notific['telgu_title'] = str(self.user.st.name)+' మీ వీడియోను ఇష్టపడ్డారు'
            notific['bengali_title'] = str(self.user.st.name)+' আপনার ভিডিও পছন্দ হয়েছে'
            notific['kannada_title'] = str(self.user.st.name)+' ನಿಮ್ಮ ವೀಡಿಯೊ ಇಷ್ಟವಾಯಿತು'
            notific['malayalam_title'] = str(self.user.st.name)+' നിങ്ങളുടെ വീഡിയോ ഇഷ്‌ടപ്പെട്ടു'
            notific['gujrati_title'] = str(self.user.st.name)+' તમારી વિડિઓ ગમી'
            notific['marathi_title'] = str(self.user.st.name)+' आपला व्हिडिओ आवडला'
            notific['notification_type'] = '5'
            if self.topic:
                if self.topic.comment:
                    notific['instance_id'] = self.topic.comment.topic.id
                else:
                    notific['instance_id'] = self.topic.topic.id
            notific['read_status'] = self.status
            notific['id'] = self.id
            notific['created_at'] = shortnaturaltime(self.created_at)
            notific['actor_profile_pic'] = self.user.st.profile_pic 

        elif self.notification_type=='6':
            notific['title'] = 'Your video byte: "' + self.topic.title + '" has been published'
            notific['hindi_title'] = 'आपका वीडियो बाइट: "' + self.topic.title + '" प्रकाशित किया गया है'
            notific['tamil_title'] = 'உங்கள் வீடியோ பைட்: "' + self.topic.title + '" வெளியிடப்பட்டுள்ளது'
            notific['telgu_title'] = 'మీ వీడియో బైట్: "' + self.topic.title + '" ప్రచురించబడింది'
            notific['bengali_title'] = 'আপনার ভিডিও বাইট: "' + self.topic.title + '" প্রকাশিত হয়েছে'
            notific['kannada_title'] = 'ನಿಮ್ಮ ವೀಡಿಯೊ ಬೈಟ್: "' + self.topic.title + '" ಪ್ರಕಟಿಸಲಾಗಿದೆ'
            notific['malayalam_title'] = 'നിങ്ങളുടെ വീഡിയോ ബൈറ്റ്: "' + self.topic.title + '" പ്രസിദ്ധീകരിച്ചു'
            notific['gujrati_title'] = 'તમારી વિડિઓ બાઇટ: "' + self.topic.title + '" પ્રકાશિત કરવામાં આવી છે'
            notific['marathi_title'] = 'आपला व्हिडिओ बाइट: "' + self.topic.title + '" प्रकाशित केले गेले आहे'
            notific['notification_type'] = '6'
            if self.topic:
            	notific['instance_id'] = self.topic.id
            else:
                notific['instance_id'] = ''
            notific['read_status'] = self.status
            notific['id'] = self.id
            notific['created_at'] = shortnaturaltime(self.created_at)
            notific['actor_profile_pic'] = ""

        elif self.notification_type=='7':
            notific['title'] = 'Your video byte: "' + self.topic.title + '" has been deleted'
            notific['hindi_title'] = 'आपका वीडियो बाइट: "' + self.topic.title + '" हटा दिया गया है'
            notific['tamil_title'] = 'உங்கள் வீடியோ பைட்: "' + self.topic.title + '" அனுப்பப்பட்டது'
            notific['telgu_title'] = 'మీ వీడియో బైట్: "' + self.topic.title + '" పంపబడింది'
            notific['bengali_title'] = 'আপনার ভিডিও বাইট: "' + self.topic.title + '" মুছে ফেলা হয়েছে'
            notific['kannada_title'] = 'ನಿಮ್ಮ ವೀಡಿಯೊ ಬೈಟ್: "' + self.topic.title + '" ಅಳಿಸಲಾಗಿದೆ'
            notific['malayalam_title'] = 'നിങ്ങളുടെ വീഡിയോ ബൈറ്റ്: "' + self.topic.title + '" ഇല്ലാതാക്കി'
            notific['gujrati_title'] = 'તમારી વિડિઓ બાઇટ: "' + self.topic.title + '" કા deletedી નાખવામાં આવી છે'
            notific['marathi_title'] = 'आपला व्हिडिओ बाइट: "' + self.topic.title + '" हटविले गेले आहे'
            notific['notification_type'] = '7'
            notific['instance_id'] = self.topic.id
            notific['read_status'] = self.status
            notific['id'] = self.id
            notific['created_at'] = shortnaturaltime(self.created_at)
            notific['actor_profile_pic'] = ""

        # elif self.notification_type=='8':
        #     notific['title'] = 'Your video byte: "' + self.topic.title + '" has been removed for payment'
        #     notific['hindi_title'] = 'आपका वीडियो बाइट: "' + self.topic.title + '" भुगतान के लिए वंचित किया गया है'
        #     notific['tamil_title'] = 'உங்கள் வீடியோ பைட்: "' + self.topic.title + '" கட்டணம் செலுத்தப்படவில்லை'
        #     notific['telgu_title'] = 'మీ వీడియో బైట్: "' + self.topic.title + '" చెల్లింపు కోసం కోల్పోయింది'
        #     notific['bengali_title'] = 'আপনার ভিডিও বাইট: "' + self.topic.title + '" has been removed for payment'
        #     notific['kannada_title'] = 'ನಿಮ್ಮ ವೀಡಿಯೊ ಬೈಟ್: "' + self.topic.title + '" has been removed for payment'
        #     notific['malayalam_title'] = 'നിങ്ങളുടെ വീഡിയോ ബൈറ്റ്: "' + self.topic.title + '" has been removed for payment'
        #     notific['gujrati_title'] = 'તમારી વિડિઓ બાઇટ: "' + self.topic.title + '" has been removed for payment'
        #     notific['marathi_title'] = 'आपला व्हिडिओ बाइट: "' + self.topic.title + '" has been removed for payment'
        #     notific['notification_type'] = '8'
        #     notific['instance_id'] = self.topic.id
        #     notific['read_status'] = self.status
        #     notific['id'] = self.id
        #     notific['created_at'] = shortnaturaltime(self.created_at)
        #     notific['actor_profile_pic'] = ""

        elif self.notification_type=='8':
            notific['title'] = 'Your video byte: "' + self.topic.title + '"  is eligible for earnings. It will be part of your payout.'
            notific['hindi_title'] = 'आपका वीडियो बाइट: "' + self.topic.title + '" मुद्रीकरण के लिए चुना गया है। इसके लिए आपको पैसे मिलेंगे।'
            notific['tamil_title'] = 'உங்கள் வீடியோ பைட்: "' + self.topic.title + '" பணமாக்குதலுக்காக தேர்ந்தெடுக்கப்பட்டது. இதற்கு நீங்கள் பணம் பெறுவீர்கள்.'
            notific['telgu_title'] = 'మీ వీడియో బైట్: "' + self.topic.title + '" డబ్బు ఆర్జన కోసం ఎంపిక చేయబడింది. దీని కోసం మీకు డబ్బు వస్తుంది.'
            notific['bengali_title'] = 'আপনার ভিডিও বাইট: "' + self.topic.title + '"  উপার্জনের যোগ্য is এটি আপনার অর্থ প্রদানের অংশ হবে।'
            notific['kannada_title'] = 'ನಿಮ್ಮ ವೀಡಿಯೊ ಬೈಟ್: "' + self.topic.title + '"  ಗಳಿಸಲು ಅರ್ಹವಾಗಿದೆ. ಇದು ನಿಮ್ಮ ಪಾವತಿಯ ಭಾಗವಾಗಿರುತ್ತದೆ.'
            notific['malayalam_title'] = 'നിങ്ങളുടെ വീഡിയോ ബൈറ്റ്: "' + self.topic.title + '"  നേടാൻ യോഗ്യതയുണ്ട്. ഇത് നിങ്ങളുടെ പേ out ട്ടിന്റെ ഭാഗമായിരിക്കും.'
            notific['gujrati_title'] = 'તમારી વિડિઓ બાઇટ: "' + self.topic.title + '"  કમાવવા માટે પાત્ર છે. તે તમારી ચૂકવણીનો એક ભાગ હશે.'
            notific['marathi_title'] = 'आपला व्हिडिओ बाइट: "' + self.topic.title + '"  कमाईसाठी पात्र आहे. तो आपल्या पेमेंटचा एक भाग असेल.'
            notific['notification_type'] = '8'
            notific['instance_id'] = self.topic.id
            notific['read_status'] = self.status
            notific['id'] = self.id
            notific['created_at'] = shortnaturaltime(self.created_at)
            notific['actor_profile_pic'] = ""

        elif self.notification_type=='9':
            notific['title'] = 'Your video byte: "' + self.topic.title + '" has been removed for payment'
            notific['hindi_title'] = 'आपका वीडियो बाइट: "' + self.topic.title + '" भुगतान के लिए वंचित किया गया है'
            notific['tamil_title'] = 'உங்கள் வீடியோ பைட்: "' + self.topic.title + '" கட்டணம் செலுத்தப்படவில்லை'
            notific['telgu_title'] = 'మీ వీడియో బైట్: "' + self.topic.title + '" చెల్లింపు కోసం కోల్పోయింది'
            notific['bengali_title'] = 'আপনার ভিডিও বাইট: "' + self.topic.title + '" অর্থ প্রদানের জন্য সরানো হয়েছে'
            notific['kannada_title'] = 'ನಿಮ್ಮ ವೀಡಿಯೊ ಬೈಟ್: "' + self.topic.title + '" ಪಾವತಿಗಾಗಿ ತೆಗೆದುಹಾಕಲಾಗಿದೆ'
            notific['malayalam_title'] = 'നിങ്ങളുടെ വീഡിയോ ബൈറ്റ്: "' + self.topic.title + '" പേയ്‌മെന്റിനായി നീക്കംചെയ്‌തു'
            notific['gujrati_title'] = 'તમારી વિડિઓ બાઇટ: "' + self.topic.title + '" ચુકવણી માટે દૂર કરવામાં આવી છે'
            notific['marathi_title'] = 'आपला व्हिडिओ बाइट: "' + self.topic.title + '" देयकासाठी काढले गेले आहे'
            notific['notification_type'] = '9'
            notific['instance_id'] = self.topic.id
            notific['read_status'] = self.status
            notific['id'] = self.id
            notific['created_at'] = shortnaturaltime(self.created_at)
            notific['actor_profile_pic'] = ""

        elif self.notification_type=='10':
            notific['title'] = str(self.user.st.name)+' has mentioned you in his comment: '+str(self.topic.comment_html)
            notific['hindi_title'] = str(self.user.st.name)+' ने अपनी टिप्पणी में आपका उल्लेख किया है: '+str(self.topic.comment_html)
            notific['tamil_title'] = str(self.user.st.name)+' அவரது கருத்தில் உங்களைக் குறிப்பிட்டுள்ளார்: '+str(self.topic.comment_html)
            notific['telgu_title'] = str(self.user.st.name)+' తన వ్యాఖ్యలో మిమ్మల్ని ప్రస్తావించారు: '+str(self.topic.comment_html)
            notific['bengali_title'] = str(self.user.st.name)+' তার মন্তব্যে আপনাকে উল্লেখ করেছে: '+str(self.topic.comment_html)
            notific['kannada_title'] = str(self.user.st.name)+' ಅವರ ಕಾಮೆಂಟ್ನಲ್ಲಿ ನಿಮ್ಮನ್ನು ಉಲ್ಲೇಖಿಸಿದ್ದಾರೆ: '+str(self.topic.comment_html)
            notific['malayalam_title'] = str(self.user.st.name)+' അവന്റെ അഭിപ്രായത്തിൽ നിങ്ങളെ പരാമർശിച്ചു: '+str(self.topic.comment_html)
            notific['gujrati_title'] = str(self.user.st.name)+' તમારી ટિપ્પણીમાં તમારો ઉલ્લેખ કર્યો છે: '+str(self.topic.comment_html)
            notific['marathi_title'] = str(self.user.st.name)+' त्याच्या टिप्पणी मध्ये आपला उल्लेख आहे: '+str(self.topic.comment_html)
            notific['notification_type'] = '10'
            notific['instance_id'] = self.topic.id
            notific['topic_id'] = self.topic.topic.id
            notific['read_status'] = self.status
            notific['id'] = self.id
            notific['created_at'] = shortnaturaltime(self.created_at)
            notific['actor_profile_pic'] = self.user.st.profile_pic

        return notific

    @staticmethod
    def get_notification_count(user_id):
        n_count =  Notification.objects.filter(for_user_id=user_id,status=0,is_active=True)
        return len(n_count)


    @staticmethod
    def get_notification(user,last_read=None,count=None):
        if not count:
            count = 5
        if last_read == None:
            notifications = Notification.objects.filter(for_user=user,is_active=True).order_by('-last_modified')[:count]
        else:
            notifications = Notification.objects.filter(for_user=user,modified_at__gte=last_read,is_active=True).order_by('-last_modified')[:count]
        Notification.objects.filter(status=0).update(status=1)
        result = []
        for notification in notifications:
            result.append(notification.get_notification_json())
        return result


class CricketMatch(models.Model):
    match_name = models.CharField(_("Match Name"),max_length=255,null=True,blank=True)
    team_1 = models.CharField(_("Team 1"),max_length=255,null=True,blank=True)
    team_1_flag = models.TextField(_("Team 1 Flag"),null=True,blank=True)
    team_2 = models.CharField(_("Team 2"),max_length=255,null=True,blank=True)
    team_2_flag = models.TextField(_("Team 2 Flag"),null=True,blank=True)
    match_datetime = models.DateTimeField(_("Match Datetime"), null=True,blank=True)
    created_at=models.DateTimeField(auto_now=False,auto_now_add=True,blank=False,null=False) # auto_now will add the current time and date whenever field is saved.
    last_modified=models.DateTimeField(auto_now=True,auto_now_add=False)
    is_active = models.BooleanField(default = True)

    class Meta:
        ordering = ['match_datetime']

    def __unicode__(self):
        return str(self.match_name)+" - "+str(self.match_datetime.date())

class Poll(models.Model):
    title = models.CharField(_("Title"),max_length=255,null=True,blank=True)
    activate_datetime = models.DateTimeField(_("Activate DateTime"), null=True,blank=True)
    deactivate_datetime = models.DateTimeField(_("Deactivate DateTime"), null=True,blank=True)
    score = models.PositiveIntegerField(_("Score"), default=0)
    bolo_score = models.PositiveIntegerField(_("Bolo Score"), default=0)
    cricketmatch = models.ForeignKey(CricketMatch, related_name='st_cricket_match',null=True,blank=True)
    created_at=models.DateTimeField(auto_now=False,auto_now_add=True,blank=False,null=False) # auto_now will add the current time and date whenever field is saved.
    last_modified=models.DateTimeField(auto_now=True,auto_now_add=False)
    is_active = models.BooleanField(default = True)
    is_evaluated = models.BooleanField(default = False)

    def __unicode__(self):
        return str(self.id)+" - "+str(self.title)

class Choice(models.Model):
    title = models.CharField(_("Title"),max_length=255,null=True,blank=True)
    image = models.CharField(_("Option Image"),max_length=255,null=True,blank=True)
    is_correct_choice = models.BooleanField(default=False)
    poll = models.ForeignKey(Poll, related_name='st_cricket_match_choice',null=False,blank=False)
    created_at=models.DateTimeField(auto_now=False,auto_now_add=True,blank=False,null=False) # auto_now will add the current time and date whenever field is saved.
    last_modified=models.DateTimeField(auto_now=True,auto_now_add=False)
    is_active = models.BooleanField(default = True)
    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return str(self.title)

class Voting(UserInfo):
    poll = models.ForeignKey(Poll, related_name='st_voting_match',null=False,blank=False)
    cricketmatch = models.ForeignKey(CricketMatch, related_name='st_voting_poll',null=True,blank=True)
    choice = models.ForeignKey(Choice, related_name='st_voting_choice',null=False,blank=False)
    is_active = models.BooleanField(default = True)

    def __unicode__(self):
        return str(self.choice)

class Leaderboard(UserInfo):
    total_score = models.PositiveIntegerField(_("Total Score"), default=0)
    total_prediction_count = models.PositiveIntegerField(_("Total Prediction"), default=0)
    correct_prediction_count = models.PositiveIntegerField(_("Correct Prediction"), default=0)
    last_rank = models.PositiveIntegerField(_("Correct Prediction"),default=0)
    current_rank = models.PositiveIntegerField(_("Correct Prediction"),null=True,blank=True)

    def __unicode__(self):
        return str(self.total_score)

# model for recording the details of video deleted
class VideoDeleted(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='st_topics')
    video_name = models.TextField(_("video_name"), null = False, blank = False)
    time_deleted = models.DateTimeField(auto_now = True, auto_now_add = False)
    plag_text = models.TextField(_("plag_text"), null = False, blank = False)

        

