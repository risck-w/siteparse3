#!/usr/bin/python
# coding=utf-8

import os
import tornado.web

from urls import urls


application = tornado.web.Application(
    handlers=urls
)