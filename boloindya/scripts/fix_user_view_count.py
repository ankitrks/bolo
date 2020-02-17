from forum.user.models import UserProfile
from forum.topic.models import Topic,VBseen,BoloActionHistory
from django.db.models import Sum
from django.contrib.contenttypes.models import ContentType
# import gc

def run():
    view_counter = 0
    all_topic= Topic.objects.filter(is_vb=True).distinct('user').order_by('user')
    total_topic = len(all_topic)
    for each_topic in all_topic:
        print "#######################   ",view_counter,"/",total_topic,"      ##########################"
        userprofile = UserProfile.objects.filter(user = each_topic.user)
        all_vb = Topic.objects.filter(user=each_topic.user, is_vb=True,is_removed = False)
        all_seen = all_vb.aggregate(Sum('view_count'))
        if all_seen.has_key('view_count__sum') and all_seen['view_count__sum']:
            print 'overall:',all_seen['view_count__sum']
            userprofile.update(own_vb_view_count = all_seen['view_count__sum'],view_count = all_seen['view_count__sum'])
        else:
            userprofile.update(own_vb_view_count = 0,view_count = 0)
        view_counter+=1


    ## will upadate when boloactionhistorya and vbseeen will be fixed

    # UserProfile.objects.filter(vb_count=0).exclude(user__in =exclude_user).update(view_count=0)
    # vb_seen_type = ContentType.objects.get(app_label='forum_topic', model='vbseen')
    # view_counter = 0
    # default_batch_size = 3000
    # for each_userprofile in all_userprofile:
    #     j=0
    #     print "#######################   ",view_counter,"/",total_user,"      ##########################"
    #     no_of_elemnts = VBseen.objects.filter(topic__user=each_userprofile.user).values_list('id',flat=True).count()
    #     print no_of_elemnts,"   ",j*default_batch_size, "     ",default_batch_size*(j+1)
    #     while(j*default_batch_size<no_of_elemnts):
    #         print j
    #         all_vb_seen_id = list(VBseen.objects.filter(topic__user=each_userprofile.user).values_list('id',flat=True))[j*default_batch_size:default_batch_size*(j+1)]
    #         print "vb id find"
    #         BoloActionHistory.objects.filter(action_object_type = vb_seen_type,action_object_id__in=all_vb_seen_id).update(user_id = each_userprofile.user.id)
    #         print "bolo_updated"
    #         view_counter+=1
    #         j+=1
    #         gc.collect()
    # view_counter=0
    # for each_userprofile in UserProfile.objects.all():
    #     print "#######################   ",view_counter,"/",total_user,"      ##########################"
    #     userprofile = UserProfile.objects.filter(user = each_userprofile.user)
    #     all_bolo_score= BoloActionHistory.objects.filter(user= each_userprofile.user).aggregate(Sum('score'))
    #     if all_bolo_score.has_key('score__sum') and all_bolo_score['score__sum']:
    #         userprofile.update(bolo_score = all_bolo_score['score__sum'])
    #     else:
    #         userprofile.update(bolo_score = 100)
    #     gc.collect()
