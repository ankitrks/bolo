# -*- coding: utf-8 -*-

from __future__ import unicode_literals

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
from drf_spirit.utils import reduce_bolo_score
from forum.user.models import UserProfile

from datetime import datetime,timedelta

language_options = (
    ('1', "English"),
    ('2', "Hindi"),
    ('3', "Tamil"),
    ('4', "Telgu"),
)

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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='st_topics',editable=False)
    category = models.ForeignKey('forum_category.Category', verbose_name=_("category"), related_name="category_topics")

    title = models.CharField(_("title"), max_length=255, blank = True, null = True)
    question_audio = models.CharField(_("audio title"), max_length=255, blank = True, null = True)
    question_video = models.CharField(_("video title"), max_length=255, blank = True, null = True)
    slug = AutoSlugField(populate_from="title", db_index=False, blank=True)
    date = models.DateTimeField(_("date"), default=timezone.now)
    last_active = models.DateTimeField(_("last active"), default=timezone.now)
    reindex_at = models.DateTimeField(_("reindex at"), default=timezone.now)
    language_id = models.CharField(choices=language_options, blank = True, null = True, max_length=10, default='0')
    question_image = models.TextField(_("Question image"),null=True,blank=True)

    is_media = models.BooleanField(default=True)
    media_duration = models.CharField(_("duration"), max_length=20, default='',null=True,blank=True)

    is_pinned = models.BooleanField(_("pinned"), default=False)
    is_globally_pinned = models.BooleanField(_("globally pinned"), default=False)
    is_closed = models.BooleanField(_("closed"), default=False)
    is_removed = models.BooleanField(default=False)
    thumbnail = models.CharField(_("thumbnail"), max_length=150, default='')
    view_count = models.PositiveIntegerField(_("views count"), default=0)
    comment_count = models.PositiveIntegerField(_("comment count"), default=0)
    total_share_count = models.PositiveIntegerField(_("Total Share count"), default=0)# self plus comment
    share_count = models.PositiveIntegerField(_("Share count"), default=0)# only topic share
    # share_user = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True, related_name='share_topic_user')
    # shared_post = models.ForeignKey('self', blank = True, null = True, related_name='user_shared_post')

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

    def delete(self):
        self.is_removed = True
        self.save()
        userprofile = UserProfile.objects.get(user = self.user)
        userprofile.question_count = F('question_count')-1
        userprofile.save()
        reduce_bolo_score(self.user.id,'create_topic')
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

    def comments(self):
        from django.utils.html import format_html

        return format_html(str('<a href="/superman/forum_comment/comment/?topic_id='+str(self.id)+'" target="_blank">'+str(self.comment_count)+'</a>'))

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
)
class SocialShare(UserInfo):
    share_type = models.CharField(choices=share_type_options, blank = True, null = True, max_length=10)
    topic = models.ForeignKey(Topic, related_name='social_share_topic_share',null=True,blank=True)
    comment = models.ForeignKey('forum_comment.Comment',related_name='social_share_topic_comment',null=True,blank=True)
    def __unicode__(self):
        return str(self.share_type)

class FCMDevice(AbstractDevice):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, related_name='%(app_label)s_%(class)s_user',editable=False)

    def __unicode__(self):
        return str(self.user)


    def register_device(self,request):
        try:
            instance = FCMDevice.objects.filter(device_id = request.POST['device_id'])
            if not len(instance):
                raise Exception
            instance.update(user = request.user,is_active = True)
            return JsonResponse({"status":"Success"},safe = False)
        except Exception as e:
            instance = FCMDevice.objects.create(device_id =request.POST['device_id'],user =request.user)
            return JsonResponse({"status":"Success"},safe = False)


    def remove_device(self,request):
        try:
            instance = FCMDevice.objects.filter(device_id = request.POST['device_id'], is_active = True, user = request.user)
            if not len(instance):
                raise Exception
            instance.update(is_active = False)
            return JsonResponse({"status":"Success"},safe = False)
        except Exception as e:
            return JsonResponse({"status":"Failed","message":"Device not found for this user"},safe = False)




class Notification(UserInfo):
    for_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,blank=True,editable=False)
    # device_id = models.CharField(_("Device Id"), max_length=255, blank = True, null = True)
    notification_type = models.CharField(_("notification_type"), max_length=5, default='1')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True,blank=True)
    topic_type = models.ForeignKey(ContentType, verbose_name=('topic type'),null=True,blank=True)
    topic_id = models.PositiveIntegerField(('object ID'),null=True,blank=True)
    topic = GenericForeignKey('topic_type', 'topic_id')

    def __unicode__(self):
        return str(self.topic)





