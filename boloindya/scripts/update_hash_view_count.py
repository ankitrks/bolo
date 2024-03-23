from forum.topic.models import Topic,TongueTwister
from datetime import datetime
from django.db.models import Q,F
from django.db.models import Sum

def run():
    all_hash_tag = TongueTwister.objects.all()
    for each_hash_tag in all_hash_tag:
        total_views = Topic.objects.filter(hash_tags = each_hash_tag).aggregate(Sum('view_count'))
        if total_views['view_count__sum']:
            seen_counter = total_views['view_count__sum']
        else:
            seen_counter = 0
        TongueTwister.objects.filter(pk=each_hash_tag.id).update(total_views = seen_counter)
