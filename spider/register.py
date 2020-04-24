#!/usr/bin/python
# coding=utf8
import json
import settings
from spider.baseSiteParser import BaseSiteParser
from Utils.Utils import find_domain
from db.redis import redis
from Utils.logs import logger


def singleton(cls):
    instance = cls()
    instance.__call__ = lambda: instance
    return instance


@singleton
class Scp(object):

    def __init__(self):
        self.craw = {}
        for cls in BaseSiteParser.__subclasses__():
            self.craw[cls.__call__().domain] = cls

    def register(self, domain, crawler):
        self.craw[domain] = crawler

    def get_craw(self, domain):
        if domain in self.craw:
            return self.craw[domain]
        return None


"""
    封装Scp解析引擎，对外暴露解析接口
    @:param url str
"""


class Sp(object):

    def __init__(self):
        pass

    @staticmethod
    def parser(url=None):
        try:
            cache_data = redis.get(url)
            if cache_data:
                logger.info('GET cache_data by redis: {0}'.format(url))
                return json.loads(cache_data)
            domain = find_domain(url=url)
            if domain is not None:
                spider = Scp.get_craw(domain=domain)()
                spider.parser()
                parser_result = spider.get_result()

                redis.set(url,
                          json.dumps(parser_result),
                          ex=settings.redis_expire)

                return parser_result
        except Exception as e:
            logger.error('Init parsing script error {0}'.format(e))

        logger.error('Cann`t find {0} script parsing engine'.format(domain))

        return {}
