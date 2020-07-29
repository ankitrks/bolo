from forum.topic.models import Topic,TongueTwister,HashtagViewCounter
from forum.comment.models import Comment
from datetime import datetime
from django.db.models import Q,F
from django.db.models import Sum,Count
from drf_spirit.utils import language_options


def run():
    duplicates = TongueTwister.objects.values('hash_tag').annotate(Count('id')) .order_by().filter(id__count__gt=1)
    print duplicates
    my_list=[]
    for each in duplicates:
        print each
        my_dict = {}
        duplicates_hash_tag_ids = TongueTwister.objects.filter(hash_tag__iexact = each['hash_tag']).order_by('id').values_list('pk',flat=True)
        print duplicates_hash_tag_ids
        base_id = duplicates_hash_tag_ids[0]
        print base_id
        duplicate_ids = duplicates_hash_tag_ids[1:]
        print duplicate_ids
        base_hashtag = TongueTwister.objects.get(pk=base_id)
        for each_duplicate_id in duplicate_ids:
            duplicate_hash_tag = TongueTwister.objects.get(pk=each_duplicate_id)
            for each_topic in Topic.objects.filter(hash_tags__id=each_duplicate_id):
                    each_topic.hash_tags.remove(duplicate_hash_tag)
                    each_topic.hash_tags.add(base_hashtag)
            for each_comment in Comment.objects.filter(hash_tags__id=each_duplicate_id):
                    each_comment.hash_tags.remove(duplicate_hash_tag)
                    each_comment.hash_tags.add(base_hashtag)
            HashtagViewCounter.objects.filter(hashtag =duplicate_hash_tag).delete()
            duplicate_hash_tag.delete()
        for each_language in language_options:
            language_specific_vb = Topic.objects.filter(hash_tags=base_hashtag, is_removed=False, is_vb=True,language_id=each_language[0])
            language_specific_seen = language_specific_vb.aggregate(Sum('view_count'))
            try:
             language_specific_hashtag, is_created = HashtagViewCounter.objects.get_or_create(hashtag=base_hashtag,language=each_language[0])
             if language_specific_seen.has_key('view_count__sum') and language_specific_seen['view_count__sum']:
                print "language_specific",each_language[1]," --> ",language_specific_seen['view_count__sum'],base_hashtag
                language_specific_hashtag.view_count = language_specific_seen['view_count__sum']
             else:
                language_specific_hashtag.view_count = 0
             language_specific_hashtag.video_count = len(language_specific_vb)
             language_specific_hashtag.save()
            except Exception as e:
                print e
                print base_hashtag 