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
from django.db.models.query import QuerySet
from django.dispatch import Signal
from diff_model import ModelDiffMixin
from redis_utils import *
from django.db.models.signals import post_save
from forum.topic.queryset import LastModifiedQueryset


post_update = Signal()



class RecordTimeStamp(models.Model):
    objects = LastModifiedQueryset.as_manager()
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

class Topic(RecordTimeStamp, ModelDiffMixin):
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

    title = models.TextField(_("title"), blank = True, null = True,db_index=True)
    question_audio = models.CharField(_("audio title"), max_length=500, blank = True, null = True)
    question_video = models.CharField(_("video title"), max_length=500, blank = True, null = True)
    slug = AutoSlugField(populate_from="title", db_index=True, blank=True)
    date = models.DateTimeField(_("date"), default=timezone.now)
    last_active = models.DateTimeField(_("last active"), default=timezone.now)
    reindex_at = models.DateTimeField(_("reindex at"), default=timezone.now)
    language_id = models.CharField(_("language"), choices=language_options, blank = True, null = True, max_length=10, default='1',db_index=True)
    question_image = models.TextField(_("Question image"),null=True,blank=True)
    is_popular = models.BooleanField(_("Popular"), default = False)
    is_pubsub_popular_push = models.BooleanField(_("Popular"), default = False)

    is_media = models.BooleanField(default=True)
    media_duration = models.CharField(_("duration"), max_length=20, default='',null=True,blank=True)
    last_commented = models.DateTimeField(_("Last Commented"),null=True,blank=True, default=timezone.now)

    is_pinned = models.BooleanField(_("pinned"), default=False)
    is_globally_pinned = models.BooleanField(_("globally pinned"), default=False)
    is_closed = models.BooleanField(_("closed"), default=False)
    is_removed = models.BooleanField(_("removed"), default=False)
    thumbnail = models.CharField(_("thumbnail"), max_length=500, blank = True, null = True, default='')
    view_count = models.PositiveIntegerField(_("views"), default=0,db_index=True)
    imp_count = models.PositiveIntegerField(_("views"), default=0,db_index=True)
    comment_count = models.PositiveIntegerField(_("comment count"), default=0,db_index=True)
    total_share_count = models.PositiveIntegerField(_("Total Share count"), default=0,db_index=True)# self plus comment
    share_count = models.PositiveIntegerField(_("Share count"), default=0,db_index=True)# only topic share
    imp_count = models.PositiveIntegerField(_("views"), default=0,db_index=True)
    topic_like_count = models.PositiveIntegerField(_("Topic Like"), default=0,db_index=True)
    topic_share_count = models.PositiveIntegerField(_("Topic Share"), default=0,db_index=True)
    # share_user = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True, related_name='share_topic_user')
    # shared_post = models.ForeignKey('self', blank = True, null = True, related_name='user_shared_post')
    is_vb = models.BooleanField(_("Is Video Bytes"), default=False)
    likes_count = models.PositiveIntegerField(_("Likes count"), default=0,db_index=True)

    is_monetized = models.BooleanField(_("monetized"), default=False)
    is_moderated = models.BooleanField(_("moderated"), default=False)
    vb_width = models.PositiveIntegerField(_("vb width"), default=0)
    vb_height = models.PositiveIntegerField(_("vb height"), default=0)
    is_thumbnail_resized = models.BooleanField(_("Thumbnail Resizd?"), default=False)

    whatsapp_share_count = models.PositiveIntegerField(null=True,blank=True,default=0)
    linkedin_share_count = models.PositiveIntegerField(null=True,blank=True,default=0)
    facebook_share_count = models.PositiveIntegerField(null=True,blank=True,default=0)
    twitter_share_count = models.PositiveIntegerField(null=True,blank=True,default=0)

    backup_url = models.TextField(_("backup url"), blank = True)
    old_backup_url = models.TextField(_("old_backup url"), blank = True)
    safe_backup_url = models.TextField(_("safe backup url"), blank = True)
    is_transcoded = models.BooleanField(default = False)
    is_transcoded_error = models.BooleanField(default = False)
    transcode_job_id = models.TextField(_("Transcode Job ID"), blank = True)
    transcode_dump = models.TextField(_("Transcode Dump"), blank = True)
    transcode_status_dump = models.TextField(_("Transcode Status Dump (Job Status)"), blank = True)

    m3u8_content = models.TextField(_("M3U8 Content"), blank = True, null = True)
    audio_m3u8_content = models.TextField(_("Audio M3U8 Content"), blank = True, null = True)
    video_m3u8_content = models.TextField(_("Video M3U8 Content"), blank = True, null = True)
    downloaded_url = models.CharField(_("downloaded URL"), max_length=500, blank = True, null = True)
    vb_playtime = models.PositiveIntegerField(null=True,blank=True,default=0,db_index=True)
    has_downloaded_url = models.BooleanField(default = False)
    vb_score = models.FloatField(_("Score"),null=True,blank=True,default=0,db_index=True)
    is_boosted = models.BooleanField(_("Super Boost"), default = False)
    popular_boosted = models.BooleanField(_("Popular Boost"), default = False)
    popular_boosted_time = models.DateTimeField(null=True,blank=True)
    boosted_till = models.PositiveIntegerField(_("boost hrs"),null=True,blank=True,default=0)
    boosted_start_time = models.DateTimeField(null=True,blank=True)
    boosted_end_time = models.DateTimeField(null=True,blank=True)
    location = models.ForeignKey(to='drf_spirit.City', blank = True, null = True, related_name='topic_location')
    
    plag_text_options = (
        ('0', "TikTok"),
        ('1', "Helo"),
        ('2', "Vigo"),
        ('3', "Tik"),
        ('4', "Tok"),
        ('5', "Vivo"),
        ('6', "ShareChat"),
        ('7', "Nojoto"),
        ('8', "Trell"),
        ('9', "ROPOSO"),
        ('10', "Likee"),
    )
    
    is_logo_checked = models.BooleanField(_("Is Logo Checked"), default=False)
    time_deleted = models.DateTimeField(blank = True, null = True)
    plag_text = models.CharField(choices = plag_text_options, blank = True, null = True, max_length = 10)

    is_violent = models.BooleanField(default=False)
    violent_content = models.PositiveIntegerField(null=True,blank=True,default=0)
    is_adult = models.BooleanField(default=False)
    adult_content = models.PositiveIntegerField(null=True,blank=True,default=0)
    logo_detected = models.BooleanField(default=False)
    profanity_collage_url = models.TextField(_("profanity collage url"), blank = True, null = True)

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
        verbose_name = _("topic")
        verbose_name_plural = _("topics")

    def update_m3u8_content(self):
        try:
            if self.question_video and '.m3u8' in self.question_video:
                if any(substring in self.question_video for substring in settings.AMAZON_ET_IDENTIFIER):
                    m3u8_url = self.question_video
                    url_split = m3u8_url.split('/')
                    audio_url = '/'.join( url_split[:-1] + ['hlsAudio'] + [url_split[-1].replace('hls_', '')] )
                    video_url = '/'.join( url_split[:-1] + ['hls1000k'] + [url_split[-1].replace('hls_', '')] )

                    self.m3u8_content = urllib2.urlopen(m3u8_url).read()
                    self.audio_m3u8_content = urllib2.urlopen(audio_url).read()
                    self.video_m3u8_content = urllib2.urlopen(video_url).read()
                    self.save()
                elif any(substring in self.question_video for substring in settings.LAMBDA_ET_IDENTIFIER):
                    self.m3u8_content = urllib2.urlopen(self.question_video).read()
                    self.audio_m3u8_content = ""
                    self.video_m3u8_content = ""
                    self.save()
                else:
                    print("M3U8 url not correct please check")
        except:
            pass

    def update_vb(self, *args, **kwargs):
        if not self.id or not self.is_transcoded:
            if self.is_vb and self.question_video and not '.m3u8' in self.question_video:
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
        try:
            if self.user.st.name:
                return format_html('<a href="/superman/forum_user/userprofile/' + str(self.user.st.id) \
                    + '/change/" target="_blank">' + self.user.st.name + '</a>' )
        except:
            pass
        return format_html('<a href="/superman/forum_user/userprofile/' + str(self.user.st.id) \
            + '/change/" target="_blank">' + self.user.username + '</a>' )

    def delete(self,is_user_deleted=False):
        if self.is_monetized:
            if self.language_id == '1':
                reduce_bolo_score(self.user.id, 'create_topic_en', self, 'deleted')
            else:
                reduce_bolo_score(self.user.id, 'create_topic', self, 'deleted')
        if not is_user_deleted:
            notify_owner = Notification.objects.create(for_user_id = self.user.id ,topic = self, \
                notification_type='7', user_id = self.user.id)
        self.is_monetized = False
        self.is_removed = True
        self.save()
        userprofile = UserProfile.objects.filter(user = self.user)
        if userprofile[0].vb_count and self.is_vb:
            userprofile.update(vb_count = F('vb_count')-1)
        return True

    def restore(self):
        self.is_removed = False
        self.save()
        userprofile = UserProfile.objects.filter(user = self.user)
        if self.is_vb: # userprofile.vb_count
            userprofile.update(vb_count = F('vb_count')+1)
        # Bolo actions will be added only when the monetization is enabled
        # add_bolo_score(self.user.id, 'create_topic', self)
        return True

    def no_monetization(self):
        # if self.is_monetized:
        self.is_monetized = False
        self.save()
        userprofile = UserProfile.objects.filter(user = self.user)
        if self.language_id == '1':
            reduce_bolo_score(self.user.id, 'create_topic_en', self, 'no_monetize')
        else:
            reduce_bolo_score(self.user.id, 'create_topic', self, 'no_monetize')
        return True
        # else:
        #     return True

    def add_monetization(self):
        self.is_removed = False
        self.is_monetized = True
        self.save()
        userprofile = UserProfile.objects.filter(user = self.user)
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
        playback_url = ''
        if  self.question_video and '.mp4' in self.question_video:
            playback_url = self.question_video
        elif self.safe_backup_url and '.mp4' in self.safe_backup_url:
            playback_url = self.safe_backup_url
        elif self.backup_url and '.mp4' in self.backup_url:
            playback_url = self.backup_url
        
        if not playback_url and self.question_video:
            playback_url = self.question_video

        if self.media_duration:
            return format_html('<a href="javascript:void(0)" onclick="playvideo(\'' + playback_url + '\')">' + self.media_duration + '</a>' )
        return format_html('<a href="javascript:void(0)" onclick="playvideo(' + playback_url + ')">play</a>' )

    def comments(self):
        if self.comment_count:
            return format_html(str('<a href="/superman/forum_comment/comment/?topic_id='+str(self.id)+'" target="_blank">' \
                + str(self.comment_count)+'</a>'))
        return 0

    def calculate_vb_score(self):
        from .utils import get_ranking_feature_weight
        score=0
        if self.user.st.is_business:
            score += get_ranking_feature_weight('business_account')
        if self.user.st.is_superstar:
            score += get_ranking_feature_weight('user_superstar')
        if self.user.st.is_popular:
            score += get_ranking_feature_weight('user_popular')
        if not self.user.st.is_superstar and not self.user.st.is_popular:
            score += get_ranking_feature_weight('user_normal')

        if self.is_boosted and self.boosted_end_time>=datetime.now():
            score += get_ranking_feature_weight('post_superboost')

        if self.popular_boosted and (self.popular_boosted_time + timedelta(days = settings.POPULAR_BOOST_TIMEDELTA)) >= datetime.now():
            score += get_ranking_feature_weight('post_popularboost')

        if self.is_popular:
            score += get_ranking_feature_weight('post_popular')
        if not self.is_boosted and not self.is_popular:
            score += get_ranking_feature_weight('post_normal')

        unique_share_count = SocialShare.objects.filter(topic_id = self.id).distinct('user_id').count()

        if self.user.st.is_superstar:
            score += get_ranking_feature_weight('superstar_topic_play')*self.imp_count
            score += get_ranking_feature_weight('superstar_topic_like')*self.topic_like_count
            score += get_ranking_feature_weight('superstar_topic_share')*unique_share_count
            score += get_ranking_feature_weight('superstar_topic_comment')*self.comment_count

        elif self.user.st.is_popular:
            score += get_ranking_feature_weight('popular_topic_play')*self.imp_count
            score += get_ranking_feature_weight('popular_topic_like')*self.topic_like_count
            score += get_ranking_feature_weight('popular_topic_share')*unique_share_count
            score += get_ranking_feature_weight('popular_topic_comment')*self.comment_count

        elif not self.user.st.is_superstar and not self.user.st.is_popular:
            score += get_ranking_feature_weight('normal_topic_play')*self.imp_count
            score += get_ranking_feature_weight('normal_topic_like')*self.topic_like_count
            score += get_ranking_feature_weight('normal_topic_share')*unique_share_count
            score += get_ranking_feature_weight('normal_topic_comment')*self.comment_count

        # post_time = (datetime.now() - self.created_at).total_seconds() #in hrs
        # if post_time > 1209600:
        #     post_time = 1209600
        # post_time = post_time/3600
        # time_decay_constant = settings.TIME_DECAY_CONSTANT
        # score = round(((time_decay_constant**2)/((float(post_time)**2)+(time_decay_constant**2)))*score ,5) #10^10 is multplied to normailze the decimal value

        threshold_value = self.get_threshold_value()
        if not self.is_popular and threshold_value and score > threshold_value:
            Topic.objects.filter(pk=self.id).update(is_popular = True, vb_score = score)
        else:
            Topic.objects.filter(pk=self.id).update(vb_score = score)
        return score

    def get_threshold_value(self):
        try:
            if self.language_id == '1' or self.language_id == '2':
                if self.user.st.is_superstar:
                    return get_ranking_feature_weight('english_n_hindi_superstar_user_threshold')
                elif self.user.st.is_popular:
                    return get_ranking_feature_weight('english_n_hindi_popular_user_threshold')
                else:
                    return get_ranking_feature_weight('english_n_hindi_normal_user_threshold')
            else:
                if self.user.st.is_superstar:
                    return get_ranking_feature_weight('other_lang_superstar_user_threshold')
                elif self.user.st.is_popular:
                    return get_ranking_feature_weight('other_lang_popular_user_threshold')
                else:
                    return get_ranking_feature_weight('other_lang_normal_user_threshold')
        except:
            return None


    def save(self):
        if self.pk:
            try:
                data = {}
                changed_fields = self.changed_fields
                for value in changed_fields:
                    data[value] = self.get_field_diff(value)[1]
                data['last_modified'] = datetime.now()
                Topic.objects.filter(pk=self.pk).update(**data)
                try:
                    post_save.send(sender=type(self), instance=self, created=False)
                except Exception as e:
                    print e
            except Exception as e:
                super(Topic , self).save()
        else:
            super(Topic , self).save()

class RankingWeight(RecordTimeStamp):
    features=models.CharField(max_length=200)
    weight= models.FloatField(default=0,null=True)

    def __unicode__(self):
        return self.features

class TopicHistory(RecordTimeStamp):
    source = models.ForeignKey('forum_topic.Topic', blank = False, null = False, related_name='topic_history')
    hash_tags = models.ManyToManyField('forum_topic.TongueTwister', verbose_name=_("hash_tags"), \
            related_name="hash_tag_topics_history",blank=True)
    title = models.TextField(_("title"), blank = True, null = True)

    def __unicode__(self):
        return str(self.title)


class VBseen(UserInfo):
    topic = models.ForeignKey(Topic, related_name='vb_seen',null=True,blank=True)
    created_at=models.DateTimeField(default=datetime.now,blank=False,null=False)
    
    def __unicode__(self):
        return unicode(str(self.topic if self.topic else 'VB'), 'utf-8')

class FVBseen(RecordTimeStamp):
    topic = models.ForeignKey(Topic, related_name='fvb_seen',null=True,blank=True)
    created_at=models.DateTimeField(default=datetime.now,blank=False,null=False)
    view_count = models.PositiveIntegerField(_("view_count"), default=0)

    def __unicode__(self):
        return unicode(str(self.topic if self.topic else 'VB'), 'utf-8')

class TongueTwister(models.Model):
    hash_tag = models.CharField(_("Hash Tag"), max_length=255, blank = True, null = True, db_index=True, unique=True)
    en_descpription = models.TextField(_("English Hash Tag Description"),blank = True, null = True)
    hi_descpription = models.TextField(_("Hindi Hash Tag Description"),blank = True, null = True)
    ta_descpription = models.TextField(_("Tamil Hash Tag Description"),blank = True, null = True)
    te_descpription = models.TextField(_("Telgu Hash Tag Description"),blank = True, null = True)
    be_descpription = models.TextField(_("Bengali Hash Tag Description"),blank = True, null = True)
    ka_descpription = models.TextField(_("Kannada Hash Tag Description"),blank = True, null = True)
    ma_descpription = models.TextField(_("Malyalam Hash Tag Description"),blank = True, null = True)
    gj_descpription = models.TextField(_("Gujrati Hash Tag Description"),blank = True, null = True)
    mt_descpription = models.TextField(_("Marathi Hash Tag Description"),blank = True, null = True)
    pb_descpription = models.TextField(_("Punjabi Hash Tag Description"),blank = True, null = True)
    od_descpription = models.TextField(_("Odia Hash Tag Description"),blank = True, null = True)
    bj_descpription = models.TextField(_("Bhojpuri Hash Tag Description"),blank = True, null = True)
    hy_descpription = models.TextField(_("Haryanvi Hash Tag Description"),blank = True, null = True)
    si_descpription = models.TextField(_("Sinhala Hash Tag Description"),blank = True, null = True)
    picture = models.CharField(_("Picture URL"),max_length=255, blank=True,null=True)
    hash_counter = models.PositiveIntegerField(default=1,null=True,blank=True,db_index=True)
    total_views = models.PositiveIntegerField(default=0,null=True,blank=True,db_index=True)
    is_blocked = models.BooleanField(default=False)
    is_popular = models.BooleanField(default=False)
    popular_date = models.DateTimeField(_("Popular Date"),null=True,blank=True)
    order = models.IntegerField(verbose_name=_('order'), default = 0)

    def __unicode__(self):
        if self.hash_tag:
            return self.hash_tag
        else:
            return "None"

    def save(self,*args, **kwargs):
        if self.is_popular:
            self.popular_date = datetime.now()
        super(TongueTwister, self).save(*args, **kwargs)

class HashtagViewCounter(models.Model):
    hashtag = models.ForeignKey('forum_topic.TongueTwister', verbose_name=_("HashTag"), related_name="hash_tag_counter",null=True,blank=True)
    language = models.CharField(_("language"), choices=language_options, blank = True, null = True, max_length=10)
    view_count = models.BigIntegerField(default = 0)
    video_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['language']
    
    def __unicode__(self):
        return str(self.hashtag)+"---"+str(self.get_language_display())

publish_options = (
    ('0', "Unpublish"),
    ('1', "Publish")
)

class JobOpening(RecordTimeStamp):
    title = models.CharField(_("Job Title"),max_length=255, blank = True, null = True)
    slug = AutoSlugField(populate_from="title", db_index=False, blank=True)
    tag_line = models.CharField(_("Tag line"),max_length=255, blank = True, null = True)
    description = models.TextField(_("Job Description"), blank= True, null = True)
    job_location = models.CharField(_("Job Location"),max_length=255, blank = True, null = True)
    expiry_date = models.DateField(_("Expiry date"),null=True,blank=True)
    publish_status = models.CharField(_("Publish"),choices = publish_options,default=1, blank = True, null = True, max_length = 10)

    def __unicode__(self):
        return str(self.title)

class JobRequest(RecordTimeStamp):
    jobOpening = models.ForeignKey(JobOpening, related_name='job_opening',blank = True, null = True)
    name = models.CharField(_("Name"), blank = True,max_length=255, null = True)
    email = models.CharField(_("Email"), blank = True,max_length=255, null = True)
    mobile = models.CharField(_("Phone Number"), blank = True,max_length=255, null = True)
    document = models.FileField(_("Upload resume"),upload_to=settings.MEDIA_UPLOAD_DOC_PATH,blank = True, null = True)
    cover_letter = models.FileField(_("Upload Cover Letter"),upload_to=settings.MEDIA_UPLOAD_DOC_PATH,blank = True, null = True)
    help_text = models.TextField(_("Help us know you better"),blank = True, null = True)
    def __unicode__(self):
        return str(self.name)
        
class ShareTopic(UserInfo):
    topic = models.ForeignKey(Topic, related_name='share_topic_topic_share',null=True,blank=True)
    comment = models.ForeignKey('forum_comment.Comment',related_name='share_topic_topic_comment',null=True,blank=True)

    def __unicode__(self):
        return str(self.topic if self.topic else self.comment)

class Like(UserInfo):
    comment = models.ForeignKey('forum_comment.Comment',related_name='like_topic_comment',null=True,blank=True)
    topic = models.ForeignKey(Topic, related_name='like_topic_share',null=True,blank=True)
    like = models.BooleanField(default = True)
    created_at=models.DateTimeField(default=datetime.now,blank=False,null=False)

    def __unicode__(self):
        return str(self.topic if self.topic else self.comment)

share_type_options = (
    ('0', "facebook"),
    ('1', "whatsapp"),
    ('2', "linkedin"),
    ('3', "twitter"),
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
        try:
            if self.user.st.name:
                name = self.user.st.name
            else:
                name = self.user.username
        except:
            name=''
        if self.notification_type=='1':
            notific['title'] = str(name)+' has posted a video: '+self.topic.title+'. Would you like to comment?'
            notific['hindi_title'] = str(name)+' ने एक वीडियो पोस्ट किया है: '+self.topic.title+'. क्या आप टिपण्णी करना चाहेंगे?'
            notific['tamil_title'] = str(name)+' ஒரு வீடியோவை வெளியிட்டுள்ளது: '+self.topic.title+' நீங்கள் கருத்து தெரிவிக்க விரும்புகிறீர்களா?'
            notific['telgu_title'] = str(name)+' ఒక వీడియోను పోస్ట్ చేసింది: '+self.topic.title+'. మీరు వ్యాఖ్యానించాలనుకుంటున్నారా?'
            notific['bengali_title'] = str(name)+' একটি ভিডিও পোস্ট করেছে: '+self.topic.title+'. আপনি মন্তব্য করতে চান?'
            notific['kannada_title'] = str(name)+' ವೀಡಿಯೊವನ್ನು ಪೋಸ್ಟ್ ಮಾಡಿದೆ: '+self.topic.title+'. ನೀವು ಕಾಮೆಂಟ್ ಮಾಡಲು ಬಯಸುವಿರಾ?'
            notific['malayalam_title'] = str(name)+' ഒരു വീഡിയോ പോസ്റ്റുചെയ്‌തു: '+self.topic.title+'. അഭിപ്രായമിടാൻ നിങ്ങൾ ആഗ്രഹിക്കുന്നുണ്ടോ?'
            notific['gujrati_title'] = str(name)+' વિડિઓ પોસ્ટ કરી છે: '+self.topic.title+'. તમે ટિપ્પણી કરવા માંગો છો?'
            notific['marathi_title'] = str(name)+' एक व्हिडिओ पोस्ट केला आहे: '+self.topic.title+'. आपण टिप्पणी देऊ इच्छिता?'
            notific['punjabi_title'] = str(name)+' ਨੇ ਇੱਕ ਵੀਡੀਓ ਪੋਸਟ ਕੀਤਾ ਹੈ: '+self.topic.title+'. ਕੀ ਤੁਸੀਂ ਟਿੱਪਣੀ ਕਰਨਾ ਚਾਹੋਗੇ?'
            notific['odia_title'] = str(name)+' ଏକ ଭିଡିଓ ପୋଷ୍ଟ କରିଛନ୍ତି |: '+self.topic.title+'. ଆପଣ ମନ୍ତବ୍ୟ ଦେବାକୁ ଚାହୁଁଛନ୍ତି କି?'
            notific['bhojpuri_title'] = str(name)+' ने एक वीडियो पोस्ट किया है: '+self.topic.title+'. क्या आप टिपण्णी करना चाहेंगे?'
            notific['haryanvi_title'] = str(name)+' ने एक वीडियो पोस्ट किया है: '+self.topic.title+'. क्या आप टिपण्णी करना चाहेंगे?'
            notific['sinhala_title'] = str(name)+' වීඩියෝවක් පළ කර ඇත: '+self.topic.title+'. අදහස් දැක්වීමට ඔබ කැමතිද?'
            
            notific['notification_type'] = '1'
            notific['instance_id'] = self.topic.id
            notific['read_status'] = self.status
            notific['id'] = self.id
            notific['created_at'] = shortnaturaltime(self.created_at)
            notific['actor_profile_pic'] = self.user.st.profile_pic

        elif self.notification_type=='2':
            notific['title'] = str(name)+' has commented on video: '+self.topic.comment+'.'
            notific['hindi_title'] = str(name)+' ने वीडियो पर टिप्पणी की है: '+self.topic.comment
            notific['tamil_title'] = str(name)+' வீடியோவில் கருத்து தெரிவித்துள்ளது: '+self.topic.comment
            notific['telgu_title'] = str(name)+' వీడియోపై వ్యాఖ్యానించారు: '+self.topic.comment
            notific['bengali_title'] = str(name)+' ভিডিওতে মন্তব্য করেছে: '+self.topic.comment+'.'
            notific['kannada_title'] = str(name)+' ವೀಡಿಯೊದಲ್ಲಿ ಕಾಮೆಂಟ್ ಮಾಡಿದ್ದಾರೆ: '+self.topic.comment+'.'
            notific['malayalam_title'] = str(name)+' വീഡിയോയിൽ അഭിപ്രായമിട്ടു: '+self.topic.comment+'.'
            notific['gujrati_title'] = str(name)+' વિડિઓ પર ટિપ્પણી કરી છે: '+self.topic.comment+'.'
            notific['marathi_title'] = str(name)+' व्हिडिओवर टिप्पणी दिली आहे: '+self.topic.comment+'.'
            notific['punjabi_title'] = str(name)+" ਵੀਡੀਓ 'ਤੇ ਟਿੱਪਣੀ ਕੀਤੀ ਹੈ: "+self.topic.comment+"."
            notific['odia_title'] = str(name)+' ଭିଡିଓ ଉପରେ ମନ୍ତବ୍ୟ ଦେଇଛନ୍ତି |: '+self.topic.comment+'.'
            notific['bhojpuri_title'] = str(name)+' ने वीडियो पर टिप्पणी की है: '+self.topic.comment
            notific['haryanvi_title'] = str(name)+' ने वीडियो पर टिप्पणी की है: '+self.topic.comment
            notific['sinhala_title'] = str(name)+' වීඩියෝවට අදහස් දක්වා ඇත: '+self.topic.comment+'.'

            
            notific['notification_type'] = '2'
            notific['instance_id'] = self.topic.id
            notific['topic_id'] = self.topic.topic.id
            notific['read_status'] = self.status
            notific['id'] = self.id
            notific['created_at'] = shortnaturaltime(self.created_at)
            notific['actor_profile_pic'] = self.user.st.profile_pic 

        elif self.notification_type=='3':
            notific['title'] = str(name)+' has commented on your video: '+self.topic.comment
            notific['hindi_title'] = str(name)+' ने आपके वीडियो पर टिप्पणी की है: '+self.topic.comment
            notific['tamil_title'] = str(name)+' உங்கள் வீடியோவில் கருத்து தெரிவித்துள்ளது: '+self.topic.comment
            notific['telgu_title'] = str(name)+' మీ వీడియోపై వ్యాఖ్యానించారు: '+self.topic.comment
            notific['bengali_title'] = str(name)+' আপনার ভিডিওতে মন্তব্য করেছে: '+self.topic.comment
            notific['kannada_title'] = str(name)+' ನಿಮ್ಮ ವೀಡಿಯೊದಲ್ಲಿ ಕಾಮೆಂಟ್ ಮಾಡಿದ್ದಾರೆ: '+self.topic.comment
            notific['malayalam_title'] = str(name)+' നിങ്ങളുടെ വീഡിയോയിൽ അഭിപ്രായമിട്ടു: '+self.topic.comment
            notific['gujrati_title'] = str(name)+' તમારી વિડિઓ પર ટિપ્પણી કરી છે: '+self.topic.comment
            notific['marathi_title'] = str(name)+' आपल्या व्हिडिओवर टिप्पणी दिली आहे: '+self.topic.comment
            notific['punjabi_title'] = str(name)+" ਨੇ ਤੁਹਾਡੇ ਵੀਡੀਓ 'ਤੇ ਟਿੱਪਣੀ ਕੀਤੀ ਹੈ: "+self.topic.comment
            notific['odia_title'] = str(name)+' ଆପଣଙ୍କର ଭିଡିଓ ଉପରେ ମନ୍ତବ୍ୟ ଦେଇଛନ୍ତି |: '+self.topic.comment
            notific['bhojpuri_title'] = str(name)+' ने आपके वीडियो पर टिप्पणी की है: '+self.topic.comment
            notific['haryanvi_title'] = str(name)+' ने आपके वीडियो पर टिप्पणी की है: '+self.topic.comment
            notific['sinhala_title'] = str(name)+' ඔබගේ වීඩියෝවට අදහස් දක්වා ඇත: '+self.topic.comment
            notific['notification_type'] = '3'
            notific['instance_id'] = self.topic.id
            notific['topic_id'] = self.topic.topic.id
            notific['read_status'] = self.status
            notific['id'] = self.id
            notific['created_at'] = shortnaturaltime(self.created_at)
            notific['actor_profile_pic'] = self.user.st.profile_pic 

        elif self.notification_type=='4':
            notific['title'] = str(name)+' followed you'
            notific['hindi_title'] = str(name)+' ने आपको फॉलो किया'
            notific['tamil_title'] = str(name)+' ஃபாலோ செய்துள்ளார்'
            notific['telgu_title'] = str(name)+' మీరు అనుసరించారు'
            notific['bengali_title'] = str(name)+' তোমাকে অনুসরণ করেছিল'
            notific['kannada_title'] = str(name)+' ನಿಮ್ಮನ್ನು ಹಿಂಬಾಲಿಸಿದರು'
            notific['malayalam_title'] = str(name)+' നിങ്ങളെ പിന്തുടർന്നു'
            notific['gujrati_title'] = str(name)+' તમારી પાછળ'
            notific['marathi_title'] = str(name)+' आपण अनुसरण'
            notific['punjabi_title'] = str(name)+' ਤੁਹਾਡੇ ਮਗਰ'
            notific['odia_title'] = str(name)+' ତୁମକୁ ଅନୁସରଣ କଲା'
            notific['bhojpuri_title'] = str(name)+' ने आपको फॉलो किया'
            notific['haryanvi_title'] = str(name)+' ने आपको फॉलो किया'
            notific['sinhala_title'] = str(name)+' ඔබව අනුගමනය කලා'
            notific['notification_type'] = '4'
            notific['instance_id'] = self.user.id
            notific['read_status'] = self.status
            notific['id'] = self.id
            notific['created_at'] = shortnaturaltime(self.created_at)
            notific['actor_profile_pic'] = self.user.st.profile_pic 

        elif self.notification_type=='5':
            notific['title'] = str(name)+' liked your video'
            notific['hindi_title'] = str(name)+' को आपका वीडियो पसंद आया'
            notific['tamil_title'] = str(name)+' உங்கள் வீடியொவை விரும்பியுள்ளார்'
            notific['telgu_title'] = str(name)+' మీ వీడియోను ఇష్టపడ్డారు'
            notific['bengali_title'] = str(name)+' আপনার ভিডিও পছন্দ হয়েছে'
            notific['kannada_title'] = str(name)+' ನಿಮ್ಮ ವೀಡಿಯೊ ಇಷ್ಟವಾಯಿತು'
            notific['malayalam_title'] = str(name)+' നിങ്ങളുടെ വീഡിയോ ഇഷ്‌ടപ്പെട്ടു'
            notific['gujrati_title'] = str(name)+' તમારી વિડિઓ ગમી'
            notific['marathi_title'] = str(name)+' आपला व्हिडिओ आवडला'
            notific['punjabi_title'] = str(name)+' ਤੁਹਾਡੀ ਵੀਡੀਓ ਪਸੰਦ'
            notific['odia_title'] = str(name)+' ତୁମର ଭିଡିଓ ପସନ୍ଦ'
            notific['bhojpuri_title'] = str(name)+' को आपका वीडियो पसंद आया'
            notific['haryanvi_title'] = str(name)+' को आपका वीडियो पसंद आया'
            notific['sinhala_title'] = str(name)+' ඔබේ වීඩියෝවට කැමතියි'
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
            notific['punjabi_title'] = 'ਤੁਹਾਡੀ ਵੀਡੀਓ ਬਾਈਟ: "' + self.topic.title + '" ਪ੍ਰਕਾਸ਼ਤ ਕੀਤਾ ਗਿਆ ਹੈ'
            notific['odia_title'] = 'ତୁମର ଭିଡିଓ ବାଇଟ୍ : "' + self.topic.title + '" ପ୍ରକାଶିତ ହୋଇଛି |'
            notific['bhojpuri_title'] = 'आपका वीडियो बाइट: "' + self.topic.title + '" प्रकाशित किया गया है'
            notific['haryanvi_title'] = 'आपका वीडियो बाइट: "' + self.topic.title + '" प्रकाशित किया गया है'
            notific['sinhala_title'] = 'ඔබේ වීඩියෝ බයිට්: "' + self.topic.title + '" ප්‍රකාශයට පත් කර ඇත'
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
            notific['punjabi_title'] = 'ਤੁਹਾਡੀ ਵੀਡੀਓ ਬਾਈਟ: "' + self.topic.title + '" ਹਟਾ ਦਿੱਤਾ ਗਿਆ ਹੈ'
            notific['odia_title'] = 'ତୁମର ଭିଡିଓ ବାଇଟ୍ : "' + self.topic.title + '" ଡିଲିଟ୍ ହୋଇଛି'
            notific['bhojpuri_title'] = 'आपका वीडियो बाइट: "' + self.topic.title + '" हटा दिया गया है'
            notific['haryanvi_title'] = 'आपका वीडियो बाइट: "' + self.topic.title + '" हटा दिया गया है'
            notific['sinhala_title'] = 'ඔබේ වීඩියෝ බයිට්: "' + self.topic.title + '" මකා දමා ඇත'
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
        #     notific['punjabi_title'] = 'Your video byte: "' + self.topic.title + '" has been removed for payment'
        #     notific['odia_title'] = 'ତୁମର ଭିଡିଓ ବାଇଟ୍ : "' + self.topic.title + '" has been removed for payment'
        #     notific['bhojpuri_title'] = 'आपका वीडियो बाइट: "' + self.topic.title + '" भुगतान के लिए वंचित किया गया है'
        #     notific['haryanvi_title'] = 'आपका वीडियो बाइट: "' + self.topic.title + '" भुगतान के लिए वंचित किया गया है'
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
            notific['punjabi_title'] = 'ਤੁਹਾਡੀ ਵੀਡੀਓ ਬਾਈਟ: "' + self.topic.title + '"  ਕਮਾਈ ਲਈ ਯੋਗ ਹੈ. ਇਹ ਤੁਹਾਡੇ ਭੁਗਤਾਨ ਦਾ ਹਿੱਸਾ ਹੋਵੇਗਾ.'
            notific['odia_title'] = 'ତୁମର ଭିଡିଓ ବାଇଟ୍ : "' + self.topic.title + '"  ରୋଜଗାର ପାଇଁ ଯୋଗ୍ୟ ଅଟେ | ଏହା ତୁମର ଦେୟର ଏକ ଅଂଶ ହେବ |.'
            notific['bhojpuri_title'] = 'आपका वीडियो बाइट: "' + self.topic.title + '" मुद्रीकरण के लिए चुना गया है। इसके लिए आपको पैसे मिलेंगे।'
            notific['haryanvi_title'] = 'आपका वीडियो बाइट: "' + self.topic.title + '" मुद्रीकरण के लिए चुना गया है। इसके लिए आपको पैसे मिलेंगे।'
            notific['sinhala_title'] = 'ඔබේ වීඩියෝ බයිට්: "' + self.topic.title  + '" ඉපැයීම් සඳහා සුදුසුකම් ලබයි. එය ඔබගේ ගෙවීම්වල කොටසක් වනු ඇත.'
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
            notific['punjabi_title'] = 'ਤੁਹਾਡੀ ਵੀਡੀਓ ਬਾਈਟ: "' + self.topic.title + '" ਭੁਗਤਾਨ ਲਈ ਹਟਾ ਦਿੱਤਾ ਗਿਆ ਹੈ'
            notific['odia_title'] = 'ତୁମର ଭିଡିଓ ବାଇଟ୍ : "' + self.topic.title + '" ଦେୟ ପାଇଁ ଅପସାରଣ କରାଯାଇଛି |'
            notific['bhojpuri_title'] = 'आपका वीडियो बाइट: "' + self.topic.title + '" भुगतान के लिए वंचित किया गया है'
            notific['haryanvi_title'] = 'आपका वीडियो बाइट: "' + self.topic.title + '" भुगतान के लिए वंचित किया गया है'
            notific['sinhala_title'] = 'ඔබේ වීඩියෝ බයිට්: "' + self.topic.title  + '" ගෙවීමෙන් ඉවත් කර ඇත'
            notific['notification_type'] = '9'
            notific['instance_id'] = self.topic.id
            notific['read_status'] = self.status
            notific['id'] = self.id
            notific['created_at'] = shortnaturaltime(self.created_at)
            notific['actor_profile_pic'] = ""

        elif self.notification_type=='10':
            notific['title'] = str(name)+' has mentioned you in his comment: '+self.topic.comment_html
            notific['hindi_title'] = str(name)+' ने अपनी टिप्पणी में आपका उल्लेख किया है: '+self.topic.comment_html
            notific['tamil_title'] = str(name)+' அவரது கருத்தில் உங்களைக் குறிப்பிட்டுள்ளார்: '+self.topic.comment_html
            notific['telgu_title'] = str(name)+' తన వ్యాఖ్యలో మిమ్మల్ని ప్రస్తావించారు: '+self.topic.comment_html
            notific['bengali_title'] = str(name)+' তার মন্তব্যে আপনাকে উল্লেখ করেছে: '+self.topic.comment_html
            notific['kannada_title'] = str(name)+' ಅವರ ಕಾಮೆಂಟ್ನಲ್ಲಿ ನಿಮ್ಮನ್ನು ಉಲ್ಲೇಖಿಸಿದ್ದಾರೆ: '+self.topic.comment_html
            notific['malayalam_title'] = str(name)+' അവന്റെ അഭിപ്രായത്തിൽ നിങ്ങളെ പരാമർശിച്ചു: '+self.topic.comment_html
            notific['gujrati_title'] = str(name)+' તમારી ટિપ્પણીમાં તમારો ઉલ્લેખ કર્યો છે: '+self.topic.comment_html
            notific['marathi_title'] = str(name)+' त्याच्या टिप्पणी मध्ये आपला उल्लेख आहे: '+self.topic.comment_html
            notific['punjabi_title'] = str(name)+' ਆਪਣੀ ਟਿੱਪਣੀ ਵਿਚ ਤੁਹਾਡਾ ਜ਼ਿਕਰ ਕੀਤਾ ਹੈ: '+self.topic.comment_html
            notific['odia_title'] = str(name)+' ତାଙ୍କ ମନ୍ତବ୍ୟରେ ଆପଣଙ୍କୁ ଉଲ୍ଲେଖ କରିଛନ୍ତି |: '+self.topic.comment_html
            notific['bhojpuri_title'] = str(name)+' ने अपनी टिप्पणी में आपका उल्लेख किया है: '+self.topic.comment_html
            notific['haryanvi_title'] = str(name)+' ने अपनी टिप्पणी में आपका उल्लेख किया है: '+self.topic.comment_html
            notific['sinhala_title'] = str(name) +' ඔහුගේ අදහස් දැක්වීමේදී ඔබව සඳහන් කර ඇත: '+self.topic.comment_html
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
# class VideoDeleted(models.Model):
#     #user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='username_topics')
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False)
#     video_name = models.TextField(_("video_name"), null = False, blank = False)
#     time_deleted = models.DateTimeField(auto_now = True, auto_now_add = False, blank = False, null = False)
#     plag_text = models.TextField(_("plag_text"), null = False, blank = False)

class TongueTwisterCounter(RecordTimeStamp):
    tongue_twister = models.ForeignKey(TongueTwister, related_name='tongue_twister_counter',null=True,blank=True)
    hash_counter = models.PositiveIntegerField(default=1,null=True,blank=True,db_index=True)
    total_views = models.PositiveIntegerField(default=0,null=True,blank=True,db_index=True)
    language_id = models.CharField(_("language"), choices=language_options, blank = True, null = True, max_length=10, default='1',db_index=True)
    
    class Meta:
        verbose_name = _("TongueTwisterCounter")
        verbose_name_plural = _("TongueTwisterCounters")

    def __unicode__(self):
        return self.tongue_twister.hash_tag

class VideoDelete(RecordTimeStamp):
    user =  models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"),editable=False,null=True,blank=True)
    video = models.ForeignKey(Topic, null=True, blank=True)


