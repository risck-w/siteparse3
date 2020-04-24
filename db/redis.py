import redis
import settings


class Redis(object):

    def __init__(self, host='localhost', port=6379, password=None, db=0, **kwargs):
        self.pool = redis.ConnectionPool(host=host, port=port, password=password, db=db)
        self.__redis = redis.Redis(connection_pool=self.pool)

    def get_redis(self):
        return self.__redis


redis = Redis(host=settings.redis_host,
              port=settings.redis_port,
              password=settings.redis_password,
              db=settings.redis_db)\
    .get_redis()
