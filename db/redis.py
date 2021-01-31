import redis
import settings
from Utils.logs import logger


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


class CreateQueue(object):

    def __init__(self, queue_name):
        self.queue_name = queue_name

    def lpush(self, value=None):
        if value is None:
            return None

        redis.lpush(self.queue_name, value)

    def rpop(self):
        try:
            data = redis.rpop(self.queue_name)
            return data
        except Exception as e:
            logger.error(e)
            return None

    def brpop(self):
        return redis.brpop(self.queue_name)

