from forum.user.models import VideoPlaytime
from forum.topic.models import Topic
from datetime import datetime, timedelta
import random


def run():
    all_old_vb_playtime = VideoPlaytime.objects.filter(timestamp__lt = datetime.now()- timedelta(days=700))
    start_date = datetime.strptime('01-'+str(datetime.now().month)+'-'+str(datetime.now().year), "%d-%m-%Y")
    for each in all_old_vb_playtime:
        vb = Topic.objects.get(pk=each.videoid)
        if vb.date > start_date:
            random_time = random_datetime(vb.date,datetime.now())
        else:
            random_time = random_datetime(start_date,datetime.now())
        VideoPlaytime.objects.filter(pk=each.id).update(timestamp = random_time)




def random_datetime(start, end):
    """Generate a random datetime between `start` and `end`"""
    return start + timedelta(
        # Get a random amount of seconds between `start` and `end`
        seconds=random.randint(0, int((end - start).total_seconds())),
    )