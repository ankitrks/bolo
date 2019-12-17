from django.contrib.auth.models import User
from forum.topic.models import Topic,Notification,Like
from forum.comment.models import Comment
from forum.user.models import Follower
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Topic)
def save_topic(sender, instance,created, **kwargs):
    try:
        if created and not instance.is_vb:
            all_follower_list = Follower.objects.filter(user_following = instance.user).values_list('user_follower_id',flat=True)
            for each in all_follower_list:
                notify = Notification.objects.create(for_user_id = each,topic = instance,notification_type='1',user = instance.user)
    except Exception as e:
        print e
        print e
        pass

@receiver(post_save, sender=Comment)
def save_comment(sender, instance,created, **kwargs):
    try:
        if created:
            all_follower_list = Follower.objects.filter(user_following = instance.user).values_list('user_follower_id',flat=True)
            for each in all_follower_list:
                if not str(each) == str(instance.topic.user.id):
                    notify = Notification.objects.create(for_user_id = each,topic = instance,notification_type='2',user = instance.user)
            notify_owner = Notification.objects.create(for_user = instance.topic.user ,topic = instance,notification_type='3',user = instance.user)
    except Exception as e:
        print e
        print e
        pass


@receiver(post_save, sender=Follower)
def save_follow(sender, instance,created, **kwargs):
    try:
        if created:
            notify = Notification.objects.create(for_user = instance.user_following,topic = instance,notification_type='4',user = instance.user_follower)
    except Exception as e:
        print e
        pass



@receiver(post_save, sender=Like)
def save_like(sender, instance,created, **kwargs):
    try:
        if created:
            # if instance.comment:
            #   notify = Notification.objects.create(for_user = instance.comment.user, topic = instance,notification_type='5',user = instance.user)
            if instance.topic:
                notify = Notification.objects.create(for_user = instance.topic.user, topic = instance,notification_type='5',user = instance.user)
    except Exception as e:
        print e
        print e
        pass

# def save_vb(sender, instance,created, **kwargs):
#   try:
#       if instance.is_vb and instance.is_transcoded:
#           notify_owner = Notification.objects.create(for_user = instance.user ,topic = instance,notification_type='6',user = instance.user)
#   except Exception as e:
#       print e
#       print e
#       pass