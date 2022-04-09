debug = False

"""
    session expire time
"""
SESSION_EXPIRE_TIME = 3600


"""
    jwt secret
"""
secret = 'GioIPy+fSVelsNacIfyBnnnc5LPwX0J0uaRQLoxJASY='

"""
    定时任务时间间隔(主要用于分词队列)，时间单位：分钟
"""
CRONTAB_TIME = 600

"""
    热点词统计频率:天
"""
COUNT_HOTWORD_DAYS = 2


"""
    Redis config
"""

redis_host = 'localhost'
redis_port = 6379
redis_password = ''
redis_db = 10

# redis expire date
redis_expire = 3
redis_timeout = 5000


"""
    Mongo config
"""

mongo_server = 'localhost'
mongo_port = 27017
mongo_database = 'siteparse3'
mongo_user = 'sp3'
mongo_password = '123456'


"""
    Mysql config
"""

mysql_host = 'localhost'
mysql_port = 3306
mysql_username = 'root'
mysql_password = '123456'
mysql_database = 'scp3'

