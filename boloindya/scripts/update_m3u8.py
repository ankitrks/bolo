from forum.topic.models import Topic
from datetime import datetime
from django.db.models import Q

def run():
    for topic in Topic.objects.filter(is_removed = False, is_vb = True)\
        .filter(Q(m3u8_content__isnull=True) | Q(m3u8_content='')).filter(date__date = datetime.today().date()):
        topic.update_m3u8_content()