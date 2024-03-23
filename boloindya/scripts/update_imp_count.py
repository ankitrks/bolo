from forum.topic.models import Topic,VBseen

def run():
    for each_topic in Topic.objects.all():
        vb_seen_count = VBseen.objects.filter(topic=each_topic,user__st__is_test_user=False).count()
        print vb_seen_count
        each_topic.imp_count = vb_seen_count
        each_topic.save()

