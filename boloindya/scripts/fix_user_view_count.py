from forum.user.models import UserProfile
from forum.topic.models import Topic,VBseen,BoloActionHistory
from django.db.models import Sum
from django.contrib.contenttypes.models import ContentType

def run():
    view_counter = 0
    all_userprofile = UserProfile.objects.all().order_by('-vb_count')
    total_user = len(all_userprofile)
    for each_userprofile in all_userprofile:
        print "#######################   ",view_counter,"/",total_user,"      ##########################"
        all_vb = Topic.objects.filter(user=each_userprofile.user, is_vb=True)
        all_seen = all_vb.aggregate(Sum('view_count'))
        if all_seen.has_key('view_count__sum') and all_seen['view_count__sum']:
            # print 'overall:',all_seen['view_count__sum']
            each_userprofile.view_count = all_seen['view_count__sum']
        else:
            each_userprofile.view_count = 0
        view_counter+=1
        each_userprofile.save()
    vb_seen_type = ContentType.objects.get(app_label='forum_topic', model='vbseen')
    view_counter = 0
    for each_userprofile in all_userprofile:
        print "#######################   ",view_counter,"/",total_user,"      ##########################"
        all_vb_seen_id = list(VBseen.objects.filter(topic__user=each_userprofile.user).values_list('id',flat=True))
        BoloActionHistory.objects.filter(action_object_type = vb_seen_type,action_object_id__in=all_vb_seen_id).update(user_id = each_userprofile.user.id)
        view_counter+=1
    view_counter=0
    for each_userprofile in all_userprofile:
        print "#######################   ",view_counter,"/",total_user,"      ##########################"
        all_bolo = BoloActionHistory.objects.filter(user= each_userprofile.user)
        all_bolo_score= all_vb.aggregate(Sum('score'))
        if all_bolo_score.has_key('score__sum') and all_bolo_score['score__sum']:
            each_userprofile.bolo_score = all_bolo_score['score__sum']
        else:
            each_userprofile.bolo_score = 100
        each_userprofile.save()


