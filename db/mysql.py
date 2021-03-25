from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import settings


mysql_host = settings.mysql_host
mysql_port = settings.mysql_port
mysql_username = settings.mysql_username
mysql_password = settings.mysql_password
mysql_database = settings.mysql_database

db_connect = "mysql+pymysql://{0}:{1}@{2}:{3}/{4}".format(mysql_username, mysql_password, mysql_host, mysql_port, mysql_database)

engine = create_engine(db_connect, pool_recycle=25200)

BaseModel = declarative_base(engine)

sessions = scoped_session(sessionmaker(bind=engine))

session = sessions()


if __name__ == '__main__':
    print(dir(BaseModel))
    print(dir(sessions))
