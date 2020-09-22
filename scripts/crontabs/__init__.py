from apscheduler.schedulers.gevent import GeventScheduler
from Utils.logs import logger
from gevent import monkey; monkey.patch_all()
from scripts.crontabs.syncParserRankToMongo import sync_data

jobs = [sync_data]


def init():

    return GeventScheduler()


def start(scheduler=None):
    if scheduler is not None:
        return scheduler.start()
    else:
        raise Exception('scheduler not init!')


logger.info('Start initing gevent scheduler')

scheduler = init()
for job in jobs:
    scheduler.add_job(job, 'interval', hours=2)
g = start(scheduler)
g.join()

logger.info('Inited gevent scheduler')

