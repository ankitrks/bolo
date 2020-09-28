from django.conf import settings
from django.utils.functional import SimpleLazyObject

import redis
from rediscluster import RedisCluster
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
        self._redis_read_only = None
        self._redis_vbseen = None
        self._redis_vbseen_read_only = None
        self._redis_logs = None
        self._redis_logs_read_only = None

        self.startup_nodes = [{"host": settings.REDIS_CL_HOST, "port": settings.REDIS_CL_PORT}]


    # def _get_neo4j(self):
    #     if not self._neo4j:
    #         self._neo4j = GraphDatabase.driver("bolt://{}:{}".format(neo4j_host, neo4j_port),
    #                                            auth=basic_auth(neo4j_user, neo4j_password))
    #     return self._neo4j

    # def neo4j(self):
    #     return SimpleLazyObject(self._get_neo4j)

    def _get_redis(self):
        if not self._redis:
            # self._redis = RedisCluster(startup_nodes=self.startup_nodes, decode_responses=True, skip_full_coverage_check=True)
            self._redis = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
        return self._redis

    def redis(self):
        return SimpleLazyObject(self._get_redis)

    def _get_redis_read_only(self):
        if not self._redis_read_only:
            # self._redis_read_only = RedisCluster(startup_nodes=self.startup_nodes, decode_responses=True, skip_full_coverage_check=True, readonly_mode=True)
            self._redis_read_only = redis.StrictRedis(host=settings.REDIS_RO_HOST, port=settings.REDIS_RO_PORT, db=settings.REDIS_RO_DB)
        return self._redis_read_only

    def redis_read_only(self):
        return SimpleLazyObject(self._get_redis_read_only)


    def _get_redis_vbseen(self):
        if not self._redis_vbseen:
            self._redis_vbseen = redis.StrictRedis(host=settings.REDIS_VBSEEN_HOST, port=settings.REDIS_VBSEEN_PORT, db=settings.REDIS_VBSEEN_DB)
        return self._redis_vbseen

    def redis_vbseen(self):
        return SimpleLazyObject(self._get_redis_vbseen)

    def _get_redis_vbseen_read_only(self):
        if not self._redis_vbseen_read_only:
            self._redis_vbseen_read_only = redis.StrictRedis(host=settings.REDIS_VBSEEN_RO_HOST, port=settings.REDIS_VBSEEN_RO_PORT, db=settings.REDIS_VBSEEN_RO_DB)
        return self._redis_vbseen_read_only

    def redis_vbseen_read_only(self):
        return SimpleLazyObject(self._get_redis_vbseen_read_only)


    def _get_redis_logs(self):
        if not self._redis_logs:
            self._redis_logs = redis.StrictRedis(host=settings.REDIS_LOGS_HOST, port=settings.REDIS_LOGS_PORT, db=settings.REDIS_LOGS_DB)
        return self._redis_logs

    def redis_logs(self):
        return SimpleLazyObject(self._get_redis_logs)

    def _get_redis_logs_read_only(self):
        if not self._redis_logs_read_only:
            self._redis_logs_read_only = redis.StrictRedis(host=settings.REDIS_LOGS_RO_HOST, port=settings.REDIS_LOGS_RO_PORT, db=settings.REDIS_LOGS_RO_DB)
        return self._redis_logs_read_only

    def redis_logs_read_only(self):
        return SimpleLazyObject(self._get_redis_logs_read_only)
