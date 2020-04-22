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
            spider = Scp.get_craw(domain=domain)
            print(spider)
            self.write(find_domain(url=url))

