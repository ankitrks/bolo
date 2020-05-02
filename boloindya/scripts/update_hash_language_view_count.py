from forum.topic.models import Topic,TongueTwister, TongueTwisterCounter
from datetime import datetime
from django.db.models import Q,F
from django.db.models import Sum
from drf_spirit.utils import language_options

def run():
    all_hash_tag = TongueTwister.objects.all()
    count = all_hash_tag.count()
    i=0
    for each_hash_tag in all_hash_tag:
        print(str(i) + '==========' + str(count))
        i+=1
        all_topic = Topic.objects.filter(hash_tags = each_hash_tag)
        total_views = all_topic.aggregate(Sum('view_count'))
        if total_views['view_count__sum']:
            seen_counter = total_views['view_count__sum']
        else:
            seen_counter = 0
        try:
            tongue=TongueTwisterCounter.objects.get(tongue_twister=each_hash_tag, language_id='0')
            tongue.hash_counter=all_topic.count()
            tongue.total_views = seen_counter
            tongue.save()
        except:
            tongue=TongueTwisterCounter()
            tongue.tongue_twister=each_hash_tag
            tongue.hash_counter=all_topic.count()
            tongue.save()
        for each in language_options:
            if each != '0':
                language_filter=all_topic.filter(language_id=each)
                total_views = language_filter.filter().aggregate(Sum('view_count'))
                if total_views['view_count__sum']:
                    seen_counter = total_views['view_count__sum']
                else:
                    seen_counter = 0
                try:
                    tongue=TongueTwisterCounter.objects.get(tongue_twister=each_hash_tag, language_id=each)
                    tongue.hash_counter=language_filter.count()
                    tongue.total_views = seen_counter
                    tongue.save()
                except:
                    tongue=TongueTwisterCounter()
                    tongue.tongue_twister=each_hash_tag
                    tongue.hash_counter=language_filter.count()
                    tongue.language_id=each
                    tongue.total_views = seen_counter
                    tongue.save()      tongue.language_id='0'
            tongue.total_views = seen_counter

