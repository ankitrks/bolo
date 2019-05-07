from django.contrib.auth.models import User
from forum.topic.models import Topic,Notification
from forum.comment.models import Comment
from forum.user.models import Follower
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Topic)
def save_topic(sender, instance,created, **kwargs):
	print "maaz"
	if created:
		all_follower_list = Follower.objects.filter(user_following = instance.user).values_list('user_follower_id',flat=True)
		for each in all_follower_list:
			notify = Notification.objects.create(for_user_id = each,topic = instance,notification_type='1')

@receiver(post_save, sender=Comment)
def save_comment(sender, instance,created, **kwargs):
	if created:
		all_follower_list = Follower.objects.filter(user_following = instance.user).values_list('user_follower_id',flat=True)
		for each in all_follower_list:
			notify = Notification.objects.create(for_user_id = each,topic = instance,notification_type='2')
