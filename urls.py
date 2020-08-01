#!/usr/bin/python
# coding=utf8

from handler.crawler import crawler_handler
from handler.user import user_login_handler, users_handler


urls = [
    (r'/craw', crawler_handler),
    (r'/user/login', user_login_handler),
    (r'/users', users_handler)
]