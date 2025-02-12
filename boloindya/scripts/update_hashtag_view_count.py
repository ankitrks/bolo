from forum.topic.models import Topic,TongueTwister,HashtagViewCounter
from django.db.models import Sum
from drf_spirit.utils import language_options

def run():
    for hash_tag in TongueTwister.objects.all():
        all_vb = Topic.objects.filter(hash_tags=hash_tag, is_removed=False, is_vb=True)
        all_seen = all_vb.aggregate(Sum('view_count'))
        if all_seen.has_key('view_count__sum') and all_seen['view_count__sum']:
            print 'overall:',all_seen['view_count__sum']
            hash_tag.view_count = all_seen['view_count__sum']
        else:
            hash_tag.view_count = 0
        hash_tag.save()
        for each_language in language_options:
            language_specific_vb = Topic.objects.filter(hash_tags=hash_tag, is_removed=False, is_vb=True,language_id=each_language[0])
            language_specific_seen = language_specific_vb.aggregate(Sum('view_count'))
            try:
             language_specific_hashtag, is_created = HashtagViewCounter.objects.get_or_create(hashtag=hash_tag,language=each_language[0])
             if language_specific_seen.has_key('view_count__sum') and language_specific_seen['view_count__sum']:
                print "language_specific",each_language[1]," --> ",language_specific_seen['view_count__sum'],hash_tag
                language_specific_hashtag.view_count = language_specific_seen['view_count__sum']
             else:
                language_specific_hashtag.view_count = 0
             language_specific_hashtag.video_count = len(language_specific_vb)
             language_specific_hashtag.save()
            except Exception as e:
                print e
                print hash_tag 
