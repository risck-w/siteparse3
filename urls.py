#!/usr/bin/python
# coding=utf8

from handler.crawler import crawler_handler


urls = [
    (r'/craw', crawler_handler)
]