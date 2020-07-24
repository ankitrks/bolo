from django.contrib.auth.models import User
from forum.topic.models import Topic,Notification,Like,TongueTwister
from forum.comment.models import Comment
from forum.user.models import Follower
from django.db.models.signals import post_save
from django.dispatch import receiver
from tasks import * # create_topic_notification, create_comment_notification, create_hash_view_count, create_thumbnail_cloudfront
from django.dispatch import Signal
post_update = Signal()
from forum.user.utils.follow_redis import get_redis_following

@receiver(post_save, sender=Topic)
def save_topic(sender, instance, created, **kwargs):
    try:
        if created:
            create_topic_notification.delay(created,instance.id)
            create_thumbnail_cloudfront.delay(instance.id)
    except Exception as e:
        pass


@receiver(post_save, sender=Comment)
def save_comment(sender, instance,created, **kwargs):
    try:
        if created:
            create_comment_notification.delay(created,instance.id)
    except Exception as e:
        pass

@receiver(post_save, sender=TongueTwister)
def save_hashtag(sender, instance,created, **kwargs):
    try:
        if created:
            create_hash_view_count.delay(created,instance.id)
    except Exception as e:
        pass

@receiver(post_save, sender=Follower)
def save_follow(sender, instance,created, **kwargs):

    try:
        if created:
            notify = Notification.objects.create(for_user = instance.user_following,topic = instance,notification_type='4',user = instance.user_follower)
    except Exception as e:
        pass

@receiver(post_save, sender=Like)
def save_like(sender, instance,created, **kwargs):
    try:
        if created:
            # if instance.comment and not instance.comment.user == instance.user:
            #   notify = Notification.objects.create(for_user = instance.comment.user, topic = instance,notification_type='5',user = instance.user)
            if instance.topic and not instance.topic.user == instance.user:
                notify = Notification.objects.create(for_user = instance.topic.user, topic = instance,notification_type='5',user = instance.user)
    except Exception as e:
        pass

# def save_vb(sender, instance,created, **kwargs):
#   try:
#       if instance.is_vb and instance.is_transcoded:
#           notify_owner = Notification.objects.create(for_user = instance.user ,topic = instance,notification_type='6',user = instance.user)
#   except Exception as e:
#       print e
#       print e
#       pass
