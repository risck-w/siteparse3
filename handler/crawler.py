#!/usr/bin/python
# coding=utf8


import tornado.web
from spider.register import Scp
from Utils.Utils import find_domain


class crawler_handler(tornado.web.RequestHandler):
    def get(self):
        url = self.get_argument('url')
        domain = find_domain(url=url)
        if url and find_domain(url=url):
            spider = Scp.get_craw(domain=domain)()
            spider.parser(url)
            data = spider.get_result()
            self.set_header('Content-type', 'application/json')
            self.write(data)

