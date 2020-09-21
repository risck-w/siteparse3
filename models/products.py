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


BaseModel.metadata.create_all(engine)