# coding=utf-8

import tornado.web
from tornado.gen import coroutine
from tornado import concurrent
from db.mongo import User
import json

from handler import executor


class user_login_handler(tornado.web.RequestHandler):

    def post(self, *args, **kwargs):
        username = json.loads(self.request.body)['username']
        password = json.loads(self.request.body)['password']

        self.set_header("Content-type", 'application/json')
        users = User.objects(username=username)
        if len(users) == 0:
            self.write({'status': 2, 'message': '用户不存在', 'username': username})
            return None

        user = users[0]
        if user.password == password:
            self.write({'status': 0, 'message': '验证成功', 'username': username})
        else:
            self.write({'status': 1, 'message': '验证失败', 'username': username})

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()


class user_add_handler(tornado.web.RequestHandler):

    def post(self, *args, **kwargs):
        username = json.loads(self.request.body)['username']
        password = json.loads(self.request.body)['password']
        user = User(username=username, password=password)
        user.save()
        self.set_header("Content-type", 'application/json')
        self.write(user.to_json())

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()