#!/usr/bin/python
# coding=utf8

import tornado.web
from spider.register import Sp


class crawler_handler(tornado.web.RequestHandler):
    def get(self):
        url = self.get_argument('url')
        data = Sp.parser(url=url)
        self.set_header('Content-type', 'application/json')
        self.write(data)
