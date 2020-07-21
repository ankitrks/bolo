import json
import logging

from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings

import connection

redis_cli = connection.redis()

logger = logging.getLogger(__name__)


def get_redis(key):
    try:
        data = redis_cli.get("bi:"+key)
        return json.loads(data) if data else None
    except Exception as e:
        logger.exception("in get_redis " + str(e))
        return None


def set_redis(key, value, set_expiry=True):
    try:
        if set_expiry:
            return redis_cli.setex("bi:"+key, settings.REDIS_EXPIRY_TIME, json.dumps(value, cls=DjangoJSONEncoder))
        else:
            return redis_cli.set("bi:"+key, json.dumps(value, cls=DjangoJSONEncoder))
    except Exception as e:
        logger.exception("in set_redis " + str(e))
        return e


def delete_redis(key):
    try:
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
