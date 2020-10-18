import json
import logging

from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings

import connection

redis_cli = connection.redis()
redis_cli_read_only = connection.redis_read_only()
redis_cli_vbseen = connection.redis_vbseen()
redis_vbseen_read_only = connection.redis_vbseen_read_only()
redis_cli_logs = connection.redis_logs()
redis_cli_logs_read_only = connection.redis_logs_read_only()
logger = logging.getLogger(__name__)



def get_redis(key):
    try:
        if 'vb_seen:' in key or 'vb_entry:' in key:
            data = redis_vbseen_read_only.get("bi:"+key)
        elif 'android_logs:' in key:
            data = redis_cli_logs_read_only.get("bi:"+key)
        else:
            data = redis_cli_read_only.get("bi:"+key)
        return json.loads(data) if data else None
    except Exception as e:
        logger.exception("in get_redis " + str(e))
        return None

def mget_redis(keys):
    try:
        updated_keys = ['bi:%s'%key for key in keys]
        data_list = redis_cli_read_only.mget(updated_keys)
        return [json.loads(data)  for data in data_list if data]
    except Exception as e:
        logger.exception("While mgetting data for redis: %s "%str(e))
        return []

def set_redis(key, value, set_expiry=True, expiry_time=None):
    try:
        if 'vb_seen:' in key or 'vb_entry:' in key:
            if set_expiry:
                expiry_time = expiry_time or settings.REDIS_EXPIRY_TIME
                return redis_cli_vbseen.setex("bi:"+key, expiry_time, json.dumps(value, cls=DjangoJSONEncoder))
            else:
                return redis_cli_vbseen.set("bi:"+key, json.dumps(value, cls=DjangoJSONEncoder))

        elif 'android_logs:' in key:
            if set_expiry:
                if expiry_time:
                    return redis_cli_logs.setex("bi:"+key, expiry_time, json.dumps(value, cls=DjangoJSONEncoder))
                if 'userprofile_counter' in key or 'lifetime_bolo_info' in key or 'last_month_bolo_info' in key or 'current_month_bolo_info' in key:
                    return redis_cli_logs.setex("bi:"+key, settings.USER_DATA_REDIS_EXPIRY_TIME, json.dumps(value, cls=DjangoJSONEncoder))
                return redis_cli_logs.setex("bi:"+key, settings.REDIS_EXPIRY_TIME, json.dumps(value, cls=DjangoJSONEncoder))
            else:
                return redis_cli_logs.set("bi:"+key, json.dumps(value, cls=DjangoJSONEncoder))
        else:
            if set_expiry:
                if expiry_time:
                    return redis_cli.setex("bi:"+key, expiry_time, json.dumps(value, cls=DjangoJSONEncoder))
                if 'userprofile_counter' in key or 'lifetime_bolo_info' in key or 'last_month_bolo_info' in key or 'current_month_bolo_info' in key:
                    return redis_cli.setex("bi:"+key, settings.USER_DATA_REDIS_EXPIRY_TIME, json.dumps(value, cls=DjangoJSONEncoder))
                return redis_cli.setex("bi:"+key, settings.REDIS_EXPIRY_TIME, json.dumps(value, cls=DjangoJSONEncoder))
            else:
                return redis_cli.set("bi:"+key, json.dumps(value, cls=DjangoJSONEncoder))
    except Exception as e:
        logger.exception("in set_redis " + str(e))
        return e


def delete_redis(key):
    try:
        if 'vb_seen:' in key or 'vb_entry:' in key:
            return redis_cli_vbseen.delete(key)
        elif 'android_logs:' in key:
            return redis_cli_logs.delete(key)
        else:
            return redis_cli.delete(key)
    except Exception as e:
        logger.exception("Error while deleting key from redis " + str(e))
        return None

def set_atomic_redis(key,value,set_expiry=True):
    with redis_cli.pipeline() as pipe:
        while True:
            try:
                pipe.watch(key)
                pipe.multi()
                if set_expiry:
                    pipe.setex("bi:"+key, settings.REDIS_EXPIRY_TIME, json.dumps(value, cls=DjangoJSONEncoder))
                else:
                    pipe.set("bi:"+key, json.dumps(value, cls=DjangoJSONEncoder))
                pipe.execute()
                pipe.unwatch()
                break
            except Exception as e:
                print e
                logger.exception("in set_atomic_redis " + str(e))



def set_s_redis(key, value):
    try:
        return redis_cli.sadd('bi:'+key, value)
    except Exception as e:
        logger.exception("in set_sredis " + str(e))


def get_smembers_redis(key):
    try:
        return redis_cli.smembers('bi:'+key)
    except Exception as e:
        logger.exception("in get_smembers_redis " + str(e))


def sremove_redis(key, element):
    try:
        redis_cli.srem('bi:'+key, element)
    except Exception as e:
        logger.exception("in get_smembers_redis " + str(e))


def incr_redis(key):
    try:
        redis_cli.incr(key)
    except:
        logger.exception("in incr_redis " + str(e))