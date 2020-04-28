#!/usr/bin/python
# coding=utf8
import json
import settings
from spider.baseSiteParser import BaseSiteParser, ScpParser
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
                spider.parser(url=url)
                parser_result = spider.get_result()
                parser_result['code'] = 0
                redis.set(url,
                          json.dumps(parser_result),
                          ex=settings.redis_expire)

                return parser_result
        except Exception as e:
            logger.error('Init {0} parsing script error {1}'.format(domain, e))

        result = ScpParser().get_params()
        result['code'] = 1
        return result
