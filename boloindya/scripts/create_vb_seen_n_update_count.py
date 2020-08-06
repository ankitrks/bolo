from forum.user.models import UserProfile, Follower
from forum.topic.models import Topic,VBseen,BoloActionHistory
from django.db.models import Sum
import connection
from redis_utils import *
import pandas as pd
from django.db.models import F
from forum.user.utils.bolo_redis import update_profile_counter
from scripts.update_vb_score import calculate_all_vb_score_and_set_post_in_redis


def run():
    try:
        all_entries = []
        all_keys = []
        # print 'Total: ', len(redis_cli.keys("bi:vb_entry:*:*"))
        for key in redis_cli.keys("bi:vb_entry:*:*"):
            print key
            try:
                data = redis_cli.get(key)
                data =  json.loads(data) if data else None
                if data:
                    all_entries += data
                    all_keys.append(key)
            except Exception as e:
                print e
        if all_entries:
            vb_entries_df = pd.DataFrame(all_entries)
            view_count = vb_entries_df['topic_id'].value_counts( ascending = True )
            aList = [VBseen(**vals) for vals in all_entries]
            print 'Bulk Create'
            VBseen.objects.bulk_create(aList, batch_size=10000)
            for key,value in view_count.items():
                Topic.objects.filter(pk=key).update(view_count = F('view_count') + value, imp_count = F('imp_count') + value)
                update_profile_counter(Topic.objects.get(pk=key).user_id,'view_count',value,True)
            for each_key in all_keys:
                try:
                    redis_cli.delete(each_key)
                except Exception as e:
                    print e
        calculate_all_vb_score_and_set_post_in_redis()

    except Exception as e:
        print e





