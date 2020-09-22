from connection_utils import ConnectionHolder

_connection = ConnectionHolder()

redis = _connection.redis
redis_read_only = _connection.redis_read_only
redis_vbseen = _connection.redis_vbseen
redis_vbseen_read_only = _connection.redis_vbseen_read_only
# neo4j = _connection.neo4j
