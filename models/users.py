from db.mysql import BaseModel, engine
from sqlalchemy import Column, String, Integer, DateTime

import datetime


class User(BaseModel):

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='用户Id')
    password = Column(String(16), nullable=False, comment='密码')
    username = Column(String(16), nullable=False, unique=True, comment='用户名')
    telphone = Column(String(11), nullable=True, comment='手机号')
    login_date = Column(DateTime, default=datetime.date.today(), comment='最近登录时间')
    sign_date = Column(DateTime, comment='注册时间')
    logout_date = Column(DateTime, comment='最近退出时间')
    modified_date = Column(DateTime, comment='最近修改时间')

    def __init__(self, username=None, password=None, telphone=None, login_date=None, logout_date=None, sign_date=None, modified_date=None):
        self.username = username,
        self.password = password,
        self.telphone = telphone,
        self.login_date = login_date,
        self.logout_date = logout_date,
        self.sign_date = sign_date,
        self.modified_date = modified_date

    def to_json(self, keys=[]):
        json_data = {}

        if len(keys) != 0:
            for key in keys:
                json_data[key] = getattr(self, key)
            return json_data
        else:
            return {
                'id': self.id,
                'username': self.username,
                'password': self.password,
                'telphone': self.telphone,
                'sign_date': self.sign_date,
                'login_date': str(self.login_date),
                'logout_date': str(self.logout_date),
                'modified_date': str(self.modified_date)
            }

BaseModel.metadata.create_all(engine)