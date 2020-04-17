from datetime import datetime, timedelta, date
# from drf_spirit.utils import add_bolo_score
from forum.topic.models import Topic
from django.apps import apps
from forum.user.models import UserProfile, Weight

def run():
    now = datetime.now()    
    last_modified_post = Topic.objects.filter(is_vb=True,is_removed=False,last_modified__gt=now-timedelta(minutes=15)).order_by('-date')
    total_elements = len(last_modified_post)
    counter=1
    for each_post in last_modified_post:
        print "###########",counter,"/",total_elements,"###########"
        print "old score:  ",each_post.vb_score
        new_score = each_post.calculate_vb_score()
        counter+=1
        print "new score:  ",new_score