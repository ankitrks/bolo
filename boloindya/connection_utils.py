from django.conf import settings
from django.utils.functional import SimpleLazyObject

import redis
# from neo4j.v1 import GraphDatabase, basic_auth

# neo4j_host = settings.NEO4J_DATABASES['default']['HOST']
# neo4j_port = settings.NEO4J_DATABASES['default']['PORT']
# neo4j_user = settings.NEO4J_DATABASES['default']['USER']
# neo4j_password = settings.NEO4J_DATABASES['default']['PASSWORD']


class ConnectionHolder:
    """
    This class will initiate connection to neo4j and redis lazily and make sure connection is established only once
    """

    def __init__(self):
        # self._neo4j = None
        self._redis = None

    # def _get_neo4j(self):
    #     if not self._neo4j:
    #         self._neo4j = GraphDatabase.driver("bolt://{}:{}".format(neo4j_host, neo4j_port),
    #                                            auth=basic_auth(neo4j_user, neo4j_password))
    #     return self._neo4j

    # def neo4j(self):
    #     return SimpleLazyObject(self._get_neo4j)

    def _get_redis(self):
        if not self._redis:
            self._redis = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
        return self._redis

    def redis(self):
        return SimpleLazyObject(self._get_redis)
