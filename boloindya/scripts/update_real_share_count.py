from datetime import datetime, timedelta, date
# from drf_spirit.utils import add_bolo_score
from forum.topic.models import Topic, VBseen, Like ,SocialShare
from django.apps import apps


def run():
	all_topic = Topic.objects.all()
	counter = 1
	for each_topic in all_topic:
		print "##################",counter,"/",len(all_topic),"##################"
		vb_seen_count = VBseen.objects.filter(topic_id=each_topic.id,user__st__is_test_user=False).count()
		like_count = Like.objects.filter(topic_id=each_topic.id,user__st__is_test_user=False,is_active=True).count()
		social_share_count = SocialShare.objects.filter(topic_id=each_topic.id,user__st__is_test_user=False).count()
		print "vb_seen_count: ", vb_seen_count
		print "like_count: ",like_count
		print "social_share_count: ",social_share_count
		Topic.objects.filter(pk=each_topic.id).update(imp_count=vb_seen_count,topic_like_count=like_count,topic_share_count=social_share_count)
		counter+=1