import json
import logging

from django.core.serializers.json import DjangoJSONEncoder

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


def set_redis(key, value, **kwargs):
    try:
        return redis_cli.set("bi:"+key, json.dumps(value, cls=DjangoJSONEncoder), **kwargs)
    except Exception as e:
        logger.exception("in set_redis " + str(e))
        return e


def delete_redis(key):
    try:
        return redis_cli.delete(key)
    except Exception as e:
        logger.exception("Error while deleting key from redis " + str(e))
        return None
