import datetime
from db.mysql import BaseModel, engine
from sqlalchemy import Column, Integer, String, DateTime


class HotWords(BaseModel):
    """
    热点词汇表
    """

    __tablename__ = 'hot_words'

    id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(String(100), nullable=False)
    num = Column(Integer, default=0)
    update_dt = Column(DateTime, default=datetime.datetime.now())

    def __init__(self, word):
        self.word = word

    def to_json(self, keys=[]):
        json_data = {}

        if len(keys) != 0:
            for key in keys:
                json_data[key] = getattr(self, key)
            return json_data
        else:
            return {
                'word': self.word,
                'num': self.num,
                'updated_dt': str(self.update_dt)
            }



class NewsWords(BaseModel):
    """
    分词存储表
    """

    __tablename__ = 'news_words'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    update_dt = Column(DateTime, default=datetime.datetime.now())

    def __init__(self, name):
        self.name = name

    def to_json(self, keys=[]):
        json_data = {}

        if len(keys) != 0:
            for key in keys:
                json_data[key] = getattr(self, key)
            return json_data
        else:
            return {
                'name': self.name,
                'updated_dt': str(self.updated_dt)
            }


class ReqUrlNameMapping(BaseModel):
    __tablename__ = 'req_url_name_mapping'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=True, index=True)
    url = Column(String(200), nullable=True)
    pdt_type = Column(String(5))
    color = Column(String(20), default='#108ee9')
    updated_dt = Column(DateTime, default=datetime.datetime.now())
    created_dt = Column(DateTime, default=datetime.datetime.now())

    def __init__(self, name, url, pdt_type, color):
        self.name = name
        self.url = url
        self.pdt_type = pdt_type
        self.color = color

    def to_json(self, keys=[]):
        json_data = {}

        if len(keys) != 0:
            for key in keys:
                json_data[key] = getattr(self, key)
            return json_data
        else:
            return {
                'name': self.name,
                'url': self.url,
                'pdt_type': self.pdt_type,
                'color': self.color,
                'updated_dt': str(self.updated_dt),
                'created_dt': str(self.created_dt)
            }


class ParseLog(BaseModel):
    __tablename__ = 'parse_log'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=True, index=True)
    author = Column(String(20), default='', index=True)
    pdt_type = Column(String(5))
    info_num = Column(Integer, default=0, index=True)
    req_url = Column(String(200), nullable=True, index=True)
    url = Column(String(500), default='')
    orig_createtime = Column(String(40), default='', nullable=True)
    updated_dt = Column(DateTime, default=datetime.datetime.now())
    created_dt = Column(DateTime, default=datetime.datetime.now())

    def __init__(self, name, req_url, author='', pdt_type='', info_num=0, url='', orig_createtime=''):
        self.name = name
        self.author = author
        self.pdt_type = pdt_type
        self.info_num = info_num
        self.req_url = req_url
        self.url = url
        self.orig_createtime = orig_createtime

    def to_json(self, keys=[]):
        json_data = {}

        if len(keys) != 0:
            for key in keys:
                json_data[key] = getattr(self, key)
            return json_data
        else:
            return {
                'id': self.id,
                'name': self.name,
                'author': self.author,
                'pdt_type': self.pdt_type,
                'info_num': self.info_num,
                'req_url': self.req_url,
                'url': self.url,
                'orig_createtime': self.orig_createtime,
                'updated_dt': self.updated_dt,
                'created_dt': self.created_dt
            }


# class ParseRank(BaseModel):
#
#     __tablename__ = 'parse_rank'
#
#     id = Column(Integer, comment='自增id',primary_key=True, autoincrement=True)
#     name = Column(String(20), comment='名称',nullable=True)
#     author = Column(String(20), comment='作者', default='')



BaseModel.metadata.create_all(engine)