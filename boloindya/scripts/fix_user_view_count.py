from forum.user.models import UserProfile
from forum.topic.models import Topic

def run():
    for each_user in UserProfile.objects.filter(is_test_user=False).order_by('-vb_count'):
    	all_vb = Topic.objects.filter(user=each_user, is_vb=True)
        all_seen = all_vb.aggregate(Sum('view_count'))
        if all_seen.has_key('view_count__sum') and all_seen['view_count__sum']:
            # print 'overall:',all_seen['view_count__sum']
            each_user.view_count = all_seen['view_count__sum']
        else:
            each_user.view_count = 0
        each_user.save()