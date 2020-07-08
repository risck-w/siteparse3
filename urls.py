#!/usr/bin/python
# coding=utf8

from handler.crawler import crawler_handler
from handler.user import user_login_handler, user_add_handler


urls = [
    (r'/craw', crawler_handler),
    (r'/user/add', user_add_handler),
    (r'/user/login', user_login_handler)
]