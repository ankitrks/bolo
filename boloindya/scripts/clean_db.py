from forum.user.models import UserProfile
from forum.topic.models import Topic,VBseen,BoloActionHistory,SocialShare,Notification
from django.contrib.auth.models import User,Group
from django.db.models import F,Q
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from forum.topic.utils import get_redis_vb_seen


def run():
    groups = list(Group.objects.all().values_list('name',flat=True))
    exclude_user_id = list(User.objects.filter(Q(groups__name__in=groups)|Q(is_superuser=True)|Q(is_staff=True)).values_list('id',flat=True))
    post_counter = 1
    print exclude_user_id
    all_user_id = list(UserProfile.objects.filter(is_test_user=True).exclude(user_id__in=exclude_user_id).values_list('user_id',flat=True))
    all_topic = Topic.objects.all().order_by('-id')
    for each_topic in all_topic:
        print "before: vbseen delete",datetime.now()
        print "#######################   ",post_counter,"/",len(all_topic),"      ##########################"
        print VBseen.objects.filter(user__st__is_test_user=True,topic_id=each_topic.id).exclude(user_id__in=exclude_user_id).delete()
        print "after: vbseen delete",datetime.now()
        post_counter+=1
    vb_seen_type = ContentType.objects.get(app_label='forum_topic', model='vbseen')
    print "before: BoloActionHistory delete 0 score",datetime.now()
    print BoloActionHistory.objects.filter(score=0).delete()
    print "after: BoloActionHistory delete 0 score",datetime.now()
    print "before: get vb seen id",datetime.now()
    all_vb_seen_id = list(VBseen.objects.all().values_list('id',flat=True))
    print "after: get vb seen id",datetime.now()
    print "before: BoloActionHistory delete object no exist",datetime.now()
    print BoloActionHistory.objects.filter(action_object_type=vb_seen_type,score=0).exclude(action_object_type=vb_seen_type,action_object_id__in=all_vb_seen_id).delete()
    print "after: BoloActionHistory delete object no exist",datetime.now()
    print "before: SocialShare of test_user",datetime.now()
    print SocialShare.objects.filter(user_id__in=all_user_id).delete()
    print "after: SocialShare of test_user",datetime.now()
    print "before: get vb SocialShare id",datetime.now()
    all_vb_social_share_id = list(SocialShare.objects.all().values_list('id',flat=True))
    print "after: get vb SocialShare id",datetime.now()
    print "before: BoloActionHistory delete object no exist",datetime.now()
    vb_share_type = ContentType.objects.get(app_label='forum_topic', model='socialshare')
    print BoloActionHistory.objects.filter(action_object_type=vb_share_type,score=0).exclude(action_object_type=vb_share_type,action_object_id__in=all_vb_social_share_id).delete()
    print "after: BoloActionHistory delete object no exist",datetime.now()
    print "before: Notification delete for test_user",datetime.now()
    Notification.objects.filter(for_user_id__in=all_user_id).delete()
    print "after: Notification delete for test_user",datetime.now()
    print "before: BoloActionHistory delete object of test_user",datetime.now()
    print BoloActionHistory.objects.filter(user_id__in=all_user_id,score=0).delete()
    print "after: BoloActionHistory delete object of test_user",datetime.now()


    print "before: BoloActionHistory delete object no exist",datetime.now()
    # for each_bolo in BoloActionHistory.objects.all():
    #     if not each_bolo.action_object and each_bolo.score=0:
    #         print each_bolo.action_object_type,'--',each_bolo.action_object_id
    #         each_bolo.delete()
    print "after: BoloActionHistory delete object no exist",datetime.now()

    print "before: BoloActionHistory clean duplicate",datetime.now()
    total_item_to_delete = 0
    default_batch_size = 10000
    j=0
    no_of_elemnts = BoloActionHistory.objects.all().count()
    while(j*default_batch_size<no_of_elemnts):
        for each_bolo in BoloActionHistory.objects.all().order_by('-id')[j*default_batch_size:default_batch_size*(j+1)+1]:
            j+=1
            all_bolo_actions = BoloActionHistory.objects.filter(user=each_bolo.user,action_object_type=each_bolo.action_object_type, action_object_id = each_bolo.action_object_id, action = each_bolo.action ).exclude(pk=each_bolo.id)
            if all_bolo_actions:
                total_item_to_delete+=len(all_bolo_actions)
                print total_item_to_delete
                print all_bolo_actions.delete()
    print "after: BoloActionHistory clean duplicate",datetime.now()
    print total_item_to_delete


    for each_user in User.objects.filter(st__is_test_user=False):
        get_redis_vb_seen(each_user.id)

