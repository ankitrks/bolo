from forum.topic.models import *
from django.contrib.auth.models import User
from forum.user.models import UserProfile
import random
from datetime import datetime, timedelta, date
from drf_spirit.utils import add_bolo_score
from forum.comment.models import Comment

def run():
    all_test_userprofile_id = UserProfile.objects.filter(is_test_user=True).values_list('user_id',flat=True)
    user_ids = list(all_test_userprofile_id)
    user_ids = random.sample(user_ids,50)
    all_test_user = User.objects.filter(pk__in =user_ids)
    action_type =['comment','like','seen','follow','share','comment_like']
    opt_action = random.choice(action_type)
    now = datetime.now()
    topic_ids = Topic.objects.filter(is_vb=True,is_removed=False).values_list('id', flat=True)
    topic_ids = list(topic_ids)
    rand_ids = random.sample(topic_ids,50)
    actionable_topic = Topic.objects.filter(id__in=rand_ids)
    for each_topic in actionable_topic:
        action_type =['comment','like','follow','share','comment_like']
        opt_action = random.choice(action_type)
        opt_action_user = random.choice(list(all_test_user))
        if opt_action =='comment':
            action_comment(opt_action_user,each_topic)
        elif opt_action == 'like':
            print each_topic,opt_action_user,'like'
        elif opt_action == 'follow':
            action_follow(opt_action_user,random.choice(User.objects.all()).id)
        elif opt_action == 'share':
            action_share(opt_action_user,topic)
            print each_topic,opt_action_user,'share'
        elif opt_action == 'comment_like':
            all_comment_list_id = Comment.objects.filter(is_removed=False).values_list('user_id',flat=True)
            comment_ids = list(all_comment_list_id)
            comment_ids = random.sample(comment_ids,50)
            all_comment = Comment.objects.filter(pk__in =user_ids)
            for each_comment in all_comment:
                action_comment_like(opt_action_user,each_comment)
    seen_topic = Topic.objects.filter(is_vb=True,is_removed=False,date__gte=now-timedelta(days=30))
    for each_seen in seen_topic:
        if each_seen.date +timedelta(minutes=10) >= now:
            number_seen = random.randrange(6,100)
        elif each_seen.date +timedelta(minutes=10) <= now and each_seen.date +timedelta(minutes=30) >= now:

        seen_profile_user_ids = list(all_test_userprofile_id)
        seen_profile_user_ids = random.sample(seen_profile_user_ids,)
        all_test_user = User.objects.filter(pk__in =user_ids)
        action_seen(opt_action_user,each_seen)







#comment
def action_comment(user,topic):
    comment_list = ['hello','maaz','azmi','waah','kya','baat','hai']
    comment = Comment()
    comment.comment       = random.choice(comment_list)
    comment.comment_html  = random.choice(comment_list)
    comment.language_id   = user.st.language
    comment.user_id       = user.id
    comment.topic_id      = topic.id
    comment.save()
    topic = Topic.objects.get(pk = topic.id)
    topic.comment_count = F('comment_count')+1
    topic.last_commented = timezone.now()
    topic.save()
    userprofile = UserProfile.objects.get(user = user.id)
    userprofile.answer_count = F('answer_count')+1
    userprofile.save()
    comment.save()
    add_bolo_score(user.id, 'reply_on_topic', comment)

#like
def action_like(user,topic):
    liked,is_created = Like.objects.get_or_create(topic = topic ,user = user)
    if is_created:
        topic.likes_count = F('likes_count')+1
        topic.save()
        add_bolo_score(user.id, 'liked', topic)
        userprofile = UserProfile.objects.get(user = user.id)
        userprofile.like_count = F('like_count')+1
        userprofile.save()

#seen
def action_seen(user,topic):
    topic.view_count = F('view_count')+1
    topic.save()
    userprofile = topic.user.st
    userprofile.view_count = F('view_count')+1
    userprofile.save()
    vbseen,is_created = VBseen.objects.get_or_create(user = user,topic = topic)
    if is_created:
        add_bolo_score(topic.user.id, 'vb_view', vbseen)

#follow
def action_follow(test_user,any_user):
    follow,is_created = Follower.objects.get_or_create(user_follower = user,user_following_id=any_user)
    userprofile = UserProfile.objects.get(user = user)
    followed_user = UserProfile.objects.get(user_id = any_user)
    if is_created:
        add_bolo_score(user.id, 'follow', userprofile)
        add_bolo_score(any_user, 'followed', followed_user)
        userprofile.follow_count = F('follow_count')+1
        userprofile.save()
        followed_user.follower_count = F('follower_count')+1
        followed_user.save()

def action_share(user, topic):
    share_type =['facebook_share','whatsapp_share','linkedin_share','twitter_share']
    share_on = random.choice(action_type)
    if share_on == 'facebook_share':
        shared = SocialShare.objects.create(topic = topic,user = user,share_type = '0')
        topic.facebook_share_count = F('facebook_share_count')+1    
        topic.total_share_count = F('total_share_count')+1
        topic.save()
        add_bolo_score(user.id, 'facebook_share', topic)
        userprofile.share_count = F('share_count')+1
        userprofile.save()
    elif share_on == 'whatsapp_share':
        shared = SocialShare.objects.create(topic = topic,user = user,share_type = '1')
        topic.whatsapp_share_count = F('whatsapp_share_count')+1
        topic.total_share_count = F('total_share_count')+1
        topic.save()
        add_bolo_score(user.id, 'whatsapp_share', topic)
        userprofile.share_count = F('share_count')+1
        userprofile.save()
    elif share_on == 'linkedin_share':
        shared = SocialShare.objects.create(topic = topic,user = user,share_type = '2')
        topic.linkedin_share_count = F('linkedin_share_count')+1
        topic.total_share_count = F('total_share_count')+1
        topic.save()
        add_bolo_score(user.id, 'linkedin_share', topic)
        userprofile.share_count = F('share_count')+1
        userprofile.save()
    elif share_on == 'twitter_share':
        shared = SocialShare.objects.create(topic = topic,user = user,share_type = '3')
        topic.twitter_share_count = F('twitter_share_count')+1
        topic.total_share_count = F('total_share_count')+1
        topic.save()
        add_bolo_score(user.id, 'twitter_share', topic)
        userprofile.share_count = F('share_count')+1
        userprofile.save()

#comment like
def action_comment_like(user,comment):
    liked,is_created = Like.objects.get_or_create(comment = comment ,user = user)
    if is_created:
        comment.likes_count = F('likes_count')+1
        comment.save()
        add_bolo_score(user.id, 'liked', comment)
        userprofile = UserProfile.objects.get(user = user.id)
        userprofile.like_count = F('like_count')+1
        userprofile.save()
    pass

