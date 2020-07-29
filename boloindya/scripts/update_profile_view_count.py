from forum.user.models import UserProfile
from forum.topic.models import Topic, VBseen, FVBseen
from django.db.models import Sum

def run():
    view_counter = 0
    all_user_id= Topic.objects.filter(is_vb=True).distinct('user').order_by('user').values_list('user_id',flat=True)
    total_topic = len(all_user_id)
    for each_user_id in all_user_id:
        print "#######################   ",view_counter,"/",total_topic,"      ##########################"
        userprofile = UserProfile.objects.filter(user_id = each_user_id)
        total_video_id = list(Topic.objects.filter(is_vb = True,is_removed=False, user_id=each_user_id).values_list('pk',flat=True))
        real_view_count = VBseen.objects.filter(topic_id__in = total_video_id).count()
        fake_view_count = FVBseen.objects.filter(topic_id__in = total_video_id).aggregate(Sum('view_count'))
        if fake_view_count.has_key('view_count__sum') and fake_view_count['view_count__sum']:
            fake_view_count = fake_view_count['view_count__sum']
        else:
            fake_view_count = 0
        print real_view_count, fake_view_count
        view_count = real_view_count + fake_view_count
        userprofile.update(own_vb_view_count = view_count,view_count = view_count)
        view_counter+=1