# coding=utf-8

import tornado.web
from tornado.gen import coroutine
from tornado import concurrent
from db.mysql import sessions
from models.users import User
import json
import datetime


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

        session = sessions()

        user = session.query(User).filter_by(username=username).first()
        if user is None:
            self.write({'status': 2, 'message': '用户不存在', 'username': username})
            return None

        if user.password == password:
            self.write({'status': 0, 'message': '验证成功', 'username': username, '_id': user.id})
        else:
            self.write({'status': 1, 'message': '用户名或密码不正确'})

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()

    def get(self, *args, **kwargs):
        self.write_error(404)


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
        telphone = json.loads(self.request.body)['telphone']

        self.set_header("Content-type", 'application/json')
        # user = User.objects(username=username).first()
        session = sessions()

        user = session.query(User).filter_by(username=username).first()
        if user:
            self.write({'status': 3, 'message': '用户名已经被注册', 'username': username})
            return None

        user = User(
            username=username,
            password=password,
            telphone=telphone,
            sign_date=datetime.date.today()
        )

        session.add(user)
        session.commit()

        self.write({'status': 0, 'message': '注册成功', 'username': username, '_id': user.id})

    def put(self, *args, **kwargs):  # 更新用户

        username = json.loads(self.request.body)['username']
        password = json.loads(self.request.body)['password']
        telphone = json.loads(self.request.body)['telphone']

        session = sessions()
        res = session.query(User).filter(username=username).update({
            User.password: password,
            User.telphone: telphone,
            User.modified_date: datetime.date.today()
        })
        session.commit()
        self.set_header("Content-type", 'application/json')
        if res >= 1:
            self.write({'status': 0, 'message': '验证成功', 'username': username})
        else:
            self.write({'status': 2, 'message': '信息更新失败'})

    def delete(self, *args, **kwargs):
        try:
            session = sessions()
            username = json.loads(self.request.body)['username']
            users = session.query(User).filter(username=username).delete()
            session.commit()
            if not users:
                self.write({'status': 2, 'message': '用户不存在', 'username': username})
            self.write({'status': 0, 'message': '删除成功', 'username': username})
        except Exception as e:
            self.write({'status': 1, 'message': '删除用户错误', 'username': username})

    def get(self, *args, **kwargs):
        self.write_error(404)
