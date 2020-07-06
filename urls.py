#!/usr/bin/python
# coding=utf8

from handler.crawler import crawler_handler, Aes_handler


urls = [
    (r'/craw', crawler_handler),
    (r'/cyberark', Aes_handler)
]