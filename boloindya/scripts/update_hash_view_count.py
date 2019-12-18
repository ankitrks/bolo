from forum.topic.models import Topic,TongueTwister
from datetime import datetime
from django.db.models import Q,F
from django.db.models import Sum

def run():
    all_hash_tag = TongueTwister.objects.all()
    for each_hash_tag in all_hash_tag:
        total_views = Topic.objects.filter(title__icontains='#'+str(each_hash_tag.hash_tag)).aggregate(Sum('view_count'))
        if total_views['view_count__sum']:
            seen_counter = total_views['view_count__sum']
        else:
            seen_counter = 0
        each_hash_tag.total_views = F('total_views')+seen_counter
        each_hash_tag.save()