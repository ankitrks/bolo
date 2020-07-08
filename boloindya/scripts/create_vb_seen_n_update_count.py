from forum.user.models import UserProfile, Follower
from forum.topic.models import Topic,VBseen,BoloActionHistory
from django.db.models import Sum
import connection
from redis_utils import *
import pandas as pd
from django.db.models import F


def run():
    try:
        all_entries = []
        all_keys = []
        for key in redis_cli.scan_iter("bi:vb_entry:*:*"):
            try:
                data = redis_cli.get(key)
                data =  json.loads(data) if data else None
                all_entries += data
                all_keys.append(key)
            except Exception as e:
                print e
        if all_entries:
            vb_entries_df = pd.DataFrame(all_entries)
            view_count = vb_entries_df['topic_id'].value_counts( ascending = True )
            aList = [VBseen(**vals) for vals in all_entries]
            VBseen.objects.bulk_create(aList, batch_size=10000)
            for key,value in view_count.items():
                Topic.objects.filter(pk=key).update(view_count = F('view_count') + value, imp_count = F('imp_count') + value)
            for each_key in all_keys:
                try:
                    redis_cli.delete(each_key)
                except Exception as e:
                    print e

    except Exception as e:
        print e





