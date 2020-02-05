from forum.topic.models import *
from forum.user.models import *
from django.contrib.auth.models import User
from django.db.models import Sum


def run():
    for each_vb in Topic.objects.filter(is_vb=True).order_by('-id'):
        all_play = VideoPlaytime.objects.filter(videoid = each_vb.id)
        all_play_time = all_play.aggregate(Sum('playtime'))
        each_vb = Topic.objects.filter(pk=each_vb.id)
        if all_play_time.has_key('playtime__sum') and all_play_time['playtime__sum']:
            print 'vb_playtime:',all_play_time['playtime__sum']
            each_vb.update(vb_playtime = all_play_time['playtime__sum'])
        else:
            each_vb.update(vb_playtime = 0)
    for each_user in UserProfile.objects.filter(is_test_user=False):
        userprofile = UserProfile.objects.filter(pk=each_user.id)
        all_spent = UserAppTimeSpend.objects.filter(user = each_user.user.id)
        all_spent_time = all_spent.aggregate(Sum('total_time'))
        if all_spent_time.has_key('total_time__sum') and all_spent_time['total_time__sum']:
            print 'user spent time:',all_spent_time['total_time__sum']
            userprofile.update(total_time_spent = all_spent_time['total_time__sum'])
        else:
            userprofile.update(total_time_spent = 0)
        all_topic = Topic.objects.filter(is_vb=True,user= each_user.user).order_by('-id')
        all_play_time = all_topic.aggregate(Sum('vb_playtime'))
        if all_play_time.has_key('vb_playtime__sum') and all_play_time['vb_playtime__sum']:
            print 'all_video_user playtime:',all_play_time['vb_playtime__sum']
            userprofile.update(total_vb_playtime = all_play_time['vb_playtime__sum'])
        else:
            userprofile.update(total_vb_playtime = 0)


