from forum.user.models import UserProfile
from forum.topic.models import Topic,VBseen,BoloActionHistory
from django.db.models import Sum
from django.contrib.contenttypes.models import ContentType

def run():
    view_counter = 0
all_topic= Topic.objects.filter(is_vb=True).order_by('-id')
total_topic = len(all_topic)
for each_topic in all_topic:
    print "#######################   ",view_counter,"/",total_topic,"      ##########################"
    seen_count = VBseen.objects.filter(topic = each_topic).count()
    Topic.objects.filter(pk=each_topic.id).update(view_count = seen_count)
    view_counter+=1

follow_counter = 0
all_user= UserProfile.objects.all().order_by('-follower_count')
total_user = len(all_user)
for each_profile in all_user:
    print "#######################   ",follow_counter,"/",total_user,"      ##########################"
    follower_count = Follower.objects.filter(user_following_id=each_profile.user.id,is_active=True).count()
    follow_count = Follower.objects.filter(user_follower_id=each_profile.user.id,is_active=True).count()
    UserProfile.objects.filter(pk=each_profile.id).update(follower_count = follower_count,follow_count=follow_count)
    follow_counter+=1