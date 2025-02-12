# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.db.models import F
from django.utils import timezone

from ..core.conf import settings
from .managers import CommentQuerySet
from drf_spirit.utils import reduce_bolo_score
from django.db.models import F,Q
from forum.user.models import UserProfile
from drf_spirit.utils import language_options
from forum.topic.models import RecordTimeStamp

# from .transcoder import transcode_media_file



COMMENT, MOVED, CLOSED, UNCLOSED, PINNED, UNPINNED = range(6)

ACTION = (
    (COMMENT, _("comment")),
    (MOVED, _("topic moved")),
    (CLOSED, _("topic closed")),
    (UNCLOSED, _("topic unclosed")),
    (PINNED, _("topic pinned")),
    (UNPINNED, _("topic unpinned")),
)


class Comment(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='st_comments',editable=False)
    topic = models.ForeignKey('forum_topic.Topic', related_name='topic_comment')
    hash_tags = models.ManyToManyField('forum_topic.TongueTwister', verbose_name=_("hash_tags"), \
            related_name="hash_tag_comment",blank=True)

    comment = models.TextField(_("comment"))
    comment_html = models.TextField(_("comment html"))
    # backup_url = models.TextField(_("backup url"))
    action = models.IntegerField(_("action"), choices=ACTION, default=COMMENT)
    date = models.DateTimeField(default=timezone.now)
    is_removed = models.BooleanField(default=False)
    is_modified = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    is_media = models.BooleanField(default=False)
    is_audio = models.BooleanField(default=False)
    media_duration = models.CharField(_("duration"), max_length=20, default='',null=True,blank=True)
    language_id = models.CharField(choices=language_options, blank = True, null = True, max_length=10, default='1')
    thumbnail = models.CharField(_("thumbnail"), max_length=150, default='')
    
    # is_transcoded = models.BooleanField(default = False)
    # transcode_dump = models.TextField(_("backup url"))

    modified_count = models.PositiveIntegerField(_("modified count"), default=0)
    likes_count = models.PositiveIntegerField(_("likes count"), default=0)
    share_count = models.PositiveIntegerField(_("share count"), default=0)

    objects = CommentQuerySet.as_manager()

    class Meta:
        ordering = ['-media_duration']
        verbose_name = _("comment")
        verbose_name_plural = _("comments")

    def __unicode__(self):
        try:
            return str(self.comment_html)
        except:
            return str(self.id)

    # def save(self, *args, **kwargs):
    #     if not self.id or not self.is_transcoded:
    #         if self.is_media and not self.is_audio:
    #             data_dump = transcode_media_file(self.comment)
    #             self.backup_url = self.comment
    #             self.transcode_dump = data_dump
    #             self.is_transcoded = True
    #     super(Comment, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('spirit:comment:find', kwargs={'pk': str(self.id), })

    def get_updated_url(self):
        if self.comment:
            return self.comment
        return '-'
        # if 'uploads' in self.comment:
        #     return self.comment.replace("boloindya", "careeranna")    
        # return self.comment.replace("careeranna", "boloindya")

    def delete(self):
        try:
            self.is_removed = True
            self.save()
            topic= self.topic
            topic.comment_count = F('comment_count')-1
            topic.save()
            userprofile = UserProfile.objects.filter(user = self.user)
            userprofile.update(answer_count = F('answer_count')-1)
            reduce_bolo_score(self.user.id, 'reply_on_topic', topic)
            return True
        except:
            return False

    @property
    def like(self):
        # *likes* is dynamically created by manager.with_likes()
        try:
            assert len(self.likes) <= 1, "Panic, too many likes"
            return self.likes[0]
        except (AttributeError, IndexError):
            return 0

    def increase_modified_count(self):
        Comment.objects\
            .filter(pk=self.pk)\
            .update(modified_count=F('modified_count') + 1)
            
    def increase_likes_count(self):
        Comment.objects\
            .filter(pk=self.pk)\
            .update(likes_count=F('likes_count') + 1)

    def decrease_likes_count(self):
        Comment.objects\
            .filter(pk=self.pk, likes_count__gt=0)\
            .update(likes_count=F('likes_count') - 1)

    @classmethod
    def create_moderation_action(cls, user, topic, action):
        # TODO: better comment_html text (map to actions), use default language
        return cls.objects.create(
            user=user,
            topic=topic,
            action=action,
            comment="action",
            comment_html="action"
        )

    @classmethod
    def get_last_for_topic(cls, topic_id):
        return (cls.objects
                .filter(topic_id=topic_id)
                .order_by('pk')
                .last())

class CommentHistory(RecordTimeStamp):
    source = models.ForeignKey('forum_comment.Comment', blank = False, null = False, related_name='comment_history')
    comment = models.TextField(_("comment"))
    comment_html = models.TextField(_("comment html"))
    hash_tags = models.ManyToManyField('forum_topic.TongueTwister', verbose_name=_("hash_tags"), \
            related_name="hash_tag_comment_history",blank=True)

    def __unicode__(self):
        return str(self.comment)