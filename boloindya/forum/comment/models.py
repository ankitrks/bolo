# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.db.models import F
from django.utils import timezone

from ..core.conf import settings
from .managers import CommentQuerySet


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

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='st_comments')
    topic = models.ForeignKey('forum_topic.Topic', related_name='topic_comment')

    comment = models.TextField(_("comment"))
    comment_html = models.TextField(_("comment html"))
    action = models.IntegerField(_("action"), choices=ACTION, default=COMMENT)
    date = models.DateTimeField(default=timezone.now)
    is_removed = models.BooleanField(default=False)
    is_modified = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    is_media = models.BooleanField(default=False)
    is_audio = models.BooleanField(default=False)
    media_duration = models.CharField(_("duration"), max_length=20, default='')
    language_id = models.CharField(_("language"), max_length=5, default='1')
    thumbnail = models.CharField(_("thumbnail"), max_length=150, default='')

    modified_count = models.PositiveIntegerField(_("modified count"), default=0)
    likes_count = models.PositiveIntegerField(_("likes count"), default=0)

    objects = CommentQuerySet.as_manager()

    class Meta:
        ordering = ['-date', '-pk']
        verbose_name = _("comment")
        verbose_name_plural = _("comments")

    def __str__(self):
        return self.comment

    def get_absolute_url(self):
        return reverse('spirit:comment:find', kwargs={'pk': str(self.id), })

    def get_updated_url(self):
        if self.comment:
            return self.comment
        return '-'
        # if 'uploads' in self.comment:
        #     return self.comment.replace("boloindya", "careeranna")    
        # return self.comment.replace("careeranna", "boloindya")

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
