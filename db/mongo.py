from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import settings
from mongoengine import connect, Document, StringField
# from mongoengine import *

server = settings.mongo_server
port = settings.mongo_port
database = settings.mongo_database
user = settings.mongo_user
password = settings.mongo_password

# connect = False 参数解决MongoClient线程安全问题
connect(db='sp3', host='mongodb://'+user+':'+password+'@'+server+':'+str(port)+'/'+database, connect=False)


class User(Document):
    """定义用户表"""
    username = StringField(max_length=20, required=True, unique=True)
    password = StringField(max_length=16, min_length=8, required=True)


