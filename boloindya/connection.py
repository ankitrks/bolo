from connection_utils import ConnectionHolder

_connection = ConnectionHolder()

redis = _connection.redis
# neo4j = _connection.neo4j
