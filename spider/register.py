#!/usr/bin/python
# coding=utf8
from spider.baseSiteParser import BaseSiteParser


def singleton(cls):
    instance = cls()
    instance.__call__ = lambda: instance
    return instance


@singleton
class Scp(object):

    def __init__(self):
        self.craw = {}
        for cls in BaseSiteParser.__subclasses__():
            self.craw[cls.__call__().domain] = cls.__call__()

    def register(self, domain, crawler):
        self.craw[domain] = crawler.__call__()

    def get_craw(self, domain):
        if domain in self.craw:
            return self.craw[domain]
        return None
