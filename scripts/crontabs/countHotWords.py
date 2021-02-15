import datetime
import time
import pandas as pd
from db.mysql import sessions as mkSessions
from models.products import HotWords, NewsWords
from Utils.logs import logger

from apscheduler.schedulers.gevent import GeventScheduler
from gevent import monkey; monkey.patch_all()
from settings import CRONTAB_TIME



def getCurrentTime():
    return time.strftime('%Y-%m-%d %H:%M:%S ',time.localtime(time.time()))



def sync_data():
    session = mkSessions()
    time_again = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M')
    newsSplitwords = session.query(NewsWords).filter(NewsWords.update_dt > time_again).all()
    news_words_list = [x.name for x in newsSplitwords]
    news_words_split = [x.split(',') for x in news_words_list]
    a = pd.DataFrame(news_words_split)
    result = a.apply(pd.value_counts)
    counts = result.sum(axis=1)
    b = counts.to_frame(name='num')
    T = b.T
    #  过滤列名字不正常的列
    other_col_names = ['...', '?', ':', '"', ',', '']
    nomal_col = T[[cs for cs in T.columns.to_list() if cs not in other_col_names and len(cs) > 1]]
    nomal_col_T = nomal_col.T
    hot_words = nomal_col_T[nomal_col_T['num'] > 1].sort_values(by=['num']).to_dict()['num']
    # 插入数据库
    if len(hot_words) > 0:
        session.execute('truncate table hot_words')
        session.commit()

        session.execute(
            HotWords.__table__.insert(),
            [{"word": x, 'num': hot_words[x],"update_dt": getCurrentTime()} for x in hot_words]
        )

        session.commit()
    else:
        logger.info('Can`t find new words')

    session.close()


def init():

    return GeventScheduler()


def start(scheduler=None):
    if scheduler is not None:
        return scheduler.start()
    else:
        raise Exception('scheduler not init!')


logger.info('Start initing gevent scheduler')

scheduler = init()

scheduler.add_job(sync_data, 'interval', seconds=CRONTAB_TIME)

g = start(scheduler)
g.join()

logger.info('Inited gevent scheduler')