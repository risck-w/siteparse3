#!/usr/bin/python
# coding=utf8

import tornado.web
from spider.register import Sp
from tornado.concurrent import run_on_executor
import tornado.gen
from handler import executor


class crawler_handler(tornado.web.RequestHandler):

    executor = executor

    @tornado.gen.coroutine
    def get(self):
        url = self.get_argument('url')
        data = yield self.crawler_parser(url)
        self.set_header('Content-type', 'application/json')
        self.write(data)

    @run_on_executor
    def crawler_parser(self, url):
        return Sp.parser(url)

