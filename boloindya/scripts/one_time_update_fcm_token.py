import connection
from redis_utils import *
import pandas as pd
from forum.topic.utils import set_redis_fcm_token


def run():
    try:
        all_user_id = []
        for key in redis_cli.keys("bi:fcm_device:*"):
            print key
            try:
                data = redis_cli.get(key)
                data =  json.loads(data) if data else None
                for each_data in data:
                    if each_data and each_data['user_id']:
                        token = each_data['reg_id']
                        if token:
                            set_redis_fcm_token(each_data['user_id'],token)
            except Exception as e:
                print e           

    except Exception as e:
        print e
