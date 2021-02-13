from apscheduler.schedulers.gevent import GeventScheduler
from Utils.logs import logger
from gevent import monkey; monkey.patch_all()
from scripts.crontabs.wordSplitToMysql import sync_data
from scripts.crontabs.countHotWords import sync_data as hot_words
from settings import CRONTAB_TIME

jobs = [sync_data, hot_words]
times = [CRONTAB_TIME, CRONTAB_TIME-1]


def init():

    return GeventScheduler()


def start(scheduler=None):
    if scheduler is not None:
        return scheduler.start()
    else:
        raise Exception('scheduler not init!')


logger.info('Start initing gevent scheduler')

scheduler = init()

time_index = 0
for job in jobs:
    scheduler.add_job(job, 'interval', minutes=times[time_index])
    time_index = int(time_index) + 1
g = start(scheduler)
g.join()

logger.info('Inited gevent scheduler')

