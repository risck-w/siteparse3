#!/usr/bin/python
# coding=utf-8

import os
import tornado.web

from urls import get_routers


def make_application():
    return tornado.web.Application(
        handlers=get_routers()
    )