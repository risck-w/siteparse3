import datetime
from db.mysql import BaseModel, engine
from sqlalchemy import Column, Integer, String, DateTime


class ParseLog(BaseModel):
    __tablename__ = 'parse_log'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=True, index=True)
    author = Column(String(20), default='', index=True)
    pdt_type = Column(String(5))
    info_num = Column(Integer, default=0, index=True)
    updated_dt = Column(DateTime, default=datetime.date.today())
    created_dt = Column(DateTime, default=datetime.date.today())

    def __init__(self, name, author='', pdt_type='', info_num=0):
        self.name = name
        self.author = author
        self.pdt_type = pdt_type
        self.info_num = info_num

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