from forum.user.models import VideoPlaytime
from forum.topic.models import Topic
from datetime import datetime


def run():
    #only testing for march
    all_objects = VideoPlaytime.objects.all()

    for obj in all_objects:
        try:
            obj.video_id = obj.videoid
            obj.save()

        except Exception as e:
            print("ID: %s, VideoID: %s" % (obj.id, obj.videoid))
            print(e)
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")