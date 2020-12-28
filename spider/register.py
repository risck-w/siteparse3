#!/usr/bin/python
# coding=utf8
import json
import settings
from spider.baseSiteParser import BaseMusicParser, BaseVodParser, BaseLiveParser, ScpParser
from spider.baseSiteParser import BaseNewsParser
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
        self.music = {}
        self.vod = {}
        self.live = {}
        self.news = {}
        for cls in BaseMusicParser.__subclasses__():
            self.music[cls.__call__().domain] = cls

        for cls in BaseVodParser.__subclasses__():
            self.vod[cls.__call__().domain] = cls

        for cls in BaseLiveParser.__subclasses__():
            self.live[cls.__call__().domain] = cls

        for cls in BaseNewsParser.__subclasses__():
            self.news[cls.__call__().domain] = cls

    def register(self, domain, crawler):
        self.music[domain] = crawler

    def _get_collection(self, scpType=None):
        if scpType == 'music':
            return self.music
        elif scpType == 'vod':
            return self.vod
        elif scpType == 'live':
            return self.live
        elif scpType == 'news':
            return self.news
        else:
            raise Exception('unKnown scpType: %s' % (scpType))

    def get_craw(self, domain, scpType=None):
        craw = self._get_collection(scpType)
        if domain in craw:
            return craw[domain]
        return None


"""
    封装Scp解析引擎，对外暴露解析接口
    @:param url str
"""


class Sp(object):

    def __init__(self):
        pass

    @staticmethod
    def parser(params={}):
        try:
            url = params.get('url')
            parse_type = params.get('parseType')
            cache_data = redis.get(url)
            if cache_data:
                logger.info('GET cache_data by redis: {0}'.format(url))
                return json.loads(cache_data)
            domain = find_domain(url=url)
            if domain is not None:
                spider = Scp.get_craw(domain=domain, scpType=parse_type)()
                spider.parser(url=url)
                parser_result = {}
                parser_result['data'] = spider.get_result()
                if not parser_result['data']:
                    raise Exception('Parse Error!')
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
