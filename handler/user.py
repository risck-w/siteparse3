# coding=utf-8

import tornado.web
from tornado.gen import coroutine
from tornado import concurrent
from db.mongo import User
import json


class user_login_handler(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header("Access-Control-Allow-Headers", "x-requested-with,authorization,origin,content-type,accept")
        self.set_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.set_header('Content-Type', 'application/json; charset=UTF-8')

    def post(self, *args, **kwargs):
        username = json.loads(self.request.body)['username']
        password = json.loads(self.request.body)['password']

        self.set_header("Content-type", 'application/json')
        user = User.objects(username=username).first()
        if user is None:
            self.write({'status': 2, 'message': '用户不存在', 'username': username})
            return None

        user = json.loads(user.to_json())
        if user['password'] == password:
            self.write({'status': 0, 'message': '验证成功', 'username': username, '_id': user["_id"]['$oid']})
        else:
            self.write({'status': 1, 'message': '用户名或密码不正确'})

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()

    def get(self, *args, **kwargs):
        pass


class users_handler(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header("Access-Control-Allow-Headers", "x-requested-with,authorization,origin,content-type,accept")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, PUT, DELETE, OPTIONS')
        self.set_header('Content-Type', 'application/json; charset=UTF-8')

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()

    def post(self, *args, **kwargs):
        username = json.loads(self.request.body)['username']
        password = json.loads(self.request.body)['password']

        self.set_header("Content-type", 'application/json')
        user = User.objects(username=username).first()
        if user:
            self.write({'status': 3, 'message': '用户名已经被注册', 'username': username})
            return None

        user = User(username=username, password=password).save()

        user = json.loads(user.to_json())
        self.write({'status': 0, 'message': '注册成功', 'username': username, '_id': user["_id"]['$oid']})

    def put(self, *args, **kwargs):  # 更新用户

        username = json.loads(self.request.body)['username']
        password = json.loads(self.request.body)['password']
        user = User.objects(username=username).update(password=password)

        self.set_header("Content-type", 'application/json')
        if user == 1:
            new_user = User.objects(username=username)
            self.write({'status': 0, 'message': '验证成功', 'username': username, '_id': new_user["_id"]['$oid']})
        else:
            self.write({'status': 2, 'message': '信息更新失败'})

    def delete(self, *args, **kwargs):
        try:
            username = json.loads(self.request.body)['username']
            params = self.get_body_arguments()
            users = User.objects(username=username).first()
            if users:
                self.write({'status': 2, 'message': '用户不存在', 'username': username})
                return None
            users.update()
        except Exception as e:
            pass

    def get(self, *args, **kwargs):
        self.write_error(404)
