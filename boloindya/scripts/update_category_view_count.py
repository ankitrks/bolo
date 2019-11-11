from forum.category.models import Category
from forum.topic.models import Topic
from django.db.models import Sum

def run():
    for each_category in Category.objects.all():
        all_vb = Topic.objects.filter(m2mcategory=each_category, is_removed=False, is_vb=True)
        all_seen = all_vb.aggregate(Sum('view_count'))
        if all_seen.has_key('view_count__sum') and all_seen['view_count__sum']:
            each_category.view_count = all_seen['view_count__sum']
        else:
            each_category.view_count = 0
        each_category.save()