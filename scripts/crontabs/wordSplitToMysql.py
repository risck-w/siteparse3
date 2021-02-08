from db.redis import redis, CreateQueue
from db.mysql import sessions
from Utils.logs import logger
import settings

"""启动分词队列的定时任务，定时向分词队列里面插入信息词条，进行当天热点词准实时分词
"""


wordSplit_queue = CreateQueue('wordSplit_queue')

sql = """
    select name from parse_log where updated_dt >= date_sub(NOW(), interval {0} minute); 
""".format(int(settings.CRONTAB_TIME) - 1)


def sync_data():
    names = sessions.execute(sql)
    names = [dict(x.items()) for x in names.fetchall()]
    if len(names) <= 0:
        logger.info('At today, no news by crawler.')
    for query in names:
        try:
            wordSplit_queue.lpush(query.get('name'))
        except Exception as e:
            logger.error(e)
