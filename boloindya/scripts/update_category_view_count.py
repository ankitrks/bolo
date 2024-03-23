from forum.category.models import Category,CategoryViewCounter
from forum.topic.models import Topic
from django.db.models import Sum
from drf_spirit.utils import language_options

def run():
    for each_category in Category.objects.all():
        all_vb = Topic.objects.filter(m2mcategory=each_category, is_removed=False, is_vb=True)
        all_seen = all_vb.aggregate(Sum('view_count'))
        if all_seen.has_key('view_count__sum') and all_seen['view_count__sum']:
            # print 'overall:',all_seen['view_count__sum']
            each_category.view_count = all_seen['view_count__sum']
        else:
            each_category.view_count = 0
        each_category.save()
        for each_language in language_options:
            language_specific_vb = Topic.objects.filter(m2mcategory=each_category, is_removed=False, is_vb=True,language_id=each_language[0])
            language_specific_seen = language_specific_vb.aggregate(Sum('view_count'))
            language_specific_category, is_created = CategoryViewCounter.objects.get_or_create(category=each_category,language=each_language[0])
            if language_specific_seen.has_key('view_count__sum') and language_specific_seen['view_count__sum']:
                # print "language_specific",each_language[1]," --> ",language_specific_seen['view_count__sum']
                language_specific_category.view_count = language_specific_seen['view_count__sum']
            else:
                language_specific_category.view_count = 0
            language_specific_category.save()
