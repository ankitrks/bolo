from forum.user.models import UserProfile
from forum.topic.models import Topic
from django.db.models import Sum

def run():
    view_counter = 0
    all_topic= Topic.objects.filter(is_vb=True).distinct('user').order_by('user')
    total_topic = len(all_topic)
    for each_topic in all_topic:
        print "#######################   ",view_counter,"/",total_topic,"      ##########################"
        userprofile = UserProfile.objects.filter(user = each_topic.user)
        all_vb = Topic.objects.filter(user=each_topic.user, is_vb=True)
        all_seen = all_vb.aggregate(Sum('view_count'))
        if all_seen.has_key('view_count__sum') and all_seen['view_count__sum']:
            print 'overall:',all_seen['view_count__sum']
            userprofile.update(own_vb_view_count = all_seen['view_count__sum'],view_count = all_seen['view_count__sum'])
        else:
            userprofile.update(own_vb_view_count = 0,view_count = 0)
        view_counter+=1