from db.mysql import BaseModel, engine
from sqlalchemy import String, Integer, Column, DateTime

import datetime

class UserMenu(BaseModel):

    __tablename__ = 'user_menu'

    userId = Column(Integer, comment='用户ID')
    menu = Column(Integer, comment='菜单id')


BaseModel.metadata.create_all(engine)