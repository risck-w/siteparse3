#!/usr/bin/python
# coding=utf8

import tornado.web
from spider.register import Sp
from tornado.concurrent import run_on_executor
import tornado.gen
from handler import executor
from Utils.Utils import get_arguments


class crawler_handler(tornado.web.RequestHandler):

    executor = executor

    @tornado.gen.coroutine
    def get(self):
        params = get_arguments(self)
        data = yield self.crawler_parser(params)
        self.set_header('Content-type', 'application/json')
        self.write(data)

    @run_on_executor
    def crawler_parser(self, params):
        return Sp.parser(params)

