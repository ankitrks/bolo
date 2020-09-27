from forum.topic.utils import set_redis_hashtag_paginated_data_with_json
from redis_utils import *
from sentry_sdk import capture_exception

def run():
    try:
        delete_redis("removed:videos")
        for key in redis_cli.keys("bi:serialized:hashtag:*:lang:*:page:*"):
            splited_key = key.split(":")
            hashtag_id = splited_key[3]
            language_id = splited_key[5]
            page_no = splited_key[7]
            set_redis_hashtag_paginated_data_with_json(key.split("bi:")[1], language_id, hashtag_id, page_no, None, True)
            print("done")
    except Exception as e:
        print(e)
        capture_exception(e)
