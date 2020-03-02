from forum.user.models import UserProfile
from forum.topic.models import VBseen,BoloActionHistory,SocialShare,Notification
from django.contrib.auth.models import User,Group
from django.db.models import F,Q
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from forum.topic.utils import get_redis_vb_seen


def run():
    groups = list(Group.objects.all().values_list('name',flat=True))
    exclude_user_id = list(User.objects.filter(Q(groups__name__in=groups)|Q(is_superuser=True)|Q(is_staff=True)).values_list('id',flat=True))
    user_counter = 1
    print exclude_user_id
    all_user_id = list(UserProfile.objects.filter(is_test_user=True).exclude(user_id__in=exclude_user_id).values_list('user_id',flat=True))
    for each_user_id in all_user_id:
        print "before: vbseen delete",datetime.now()
        print "#######################   ",user_counter,"/",len(all_user_id),"      ##########################"
        VBseen.objects.filter(user_id=each_user_id).delete()
        print "after: vbseen delete",datetime.now()
        user_counter+=1
    vb_seen_type = ContentType.objects.get(app_label='forum_topic', model='vbseen')
    print "before: BoloActionHistory delete 0 score",datetime.now()
    BoloActionHistory.objects.filter(score=0).delete()
    print "after: BoloActionHistory delete 0 score",datetime.now()
    print "before: get vb seen id",datetime.now()
    all_vb_seen_id = list(VBseen.objects.all().values_list('id',flat=True))
    print "after: get vb seen id",datetime.now()
    print "before: BoloActionHistory delete object no exist",datetime.now()
    BoloActionHistory.objects.filter(action_object_type=vb_seen_type).exclude(action_object_type=vb_seen_type,action_object_id__in=all_vb_seen_id).delete()
    print "after: BoloActionHistory delete object no exist",datetime.now()
    print "before: SocialShare of test_user",datetime.now()
    SocialShare.objects.filter(user_id__in=all_user_id).delete()
    print "after: SocialShare of test_user",datetime.now()
    print "before: get vb SocialShare id",datetime.now()
    all_vb_social_share_id = list(SocialShare.objects.all().values_list('id',flat=True))
    print "after: get vb SocialShare id",datetime.now()
    print "before: BoloActionHistory delete object no exist",datetime.now()
    vb_share_type = ContentType.objects.get(app_label='forum_topic', model='socialshare')
    BoloActionHistory.objects.filter(action_object_type=vb_share_type).exclude(action_object_type=vb_share_type,action_object_id__in=all_vb_social_share_id).delete()
    print "after: BoloActionHistory delete object no exist",datetime.now()
    print "before: Notification delete for test_user",datetime.now()
    Notification.objects.filter(for_user_id__in=all_user_id).delete()
    print "after: Notification delete for test_user",datetime.now()
    print "before: BoloActionHistory delete object of test_user",datetime.now()
    BoloActionHistory.objects.filter(user_id__in=all_user_id,score=0).delete()
    print "after: BoloActionHistory delete object of test_user",datetime.now()


    print "before: BoloActionHistory delete object no exist",datetime.now()
    for each_bolo in BoloActionHistory.objects.all():
        if not each_bolo.action_object:
            print each_bolo.action_object_type,'--',each_bolo.action_object_id
            each_bolo.delete()
    print "after: BoloActionHistory delete object no exist",datetime.now()

    for each_user in User.objects.filter(st__is_test_user=False):
        get_redis_vb_seen(each_user.id)

