#!/usr/bin/python
# coding=utf8
from spider.baseSiteParser import BaseSiteParser
from Utils.Utils import find_domain
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
            domain = find_domain(url=url)
            if domain is not None:
                spider = Scp.get_craw(domain=domain)()
                spider.parser()
                return spider.get_result()
        except Exception as e:
            logger.error('Init parsing script error {0}'.format(e))

        logger.error('Cann`t find {0} script parsing engine'.format(domain))

        return {}
