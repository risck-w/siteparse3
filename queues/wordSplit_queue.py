import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))

import jieba
from Utils.logs import logger
from db.redis import redis, CreateQueue
from db.mysql import sessions as mkSessions
from models.products import NewsWords


wordSplit_queue = CreateQueue('wordSplit_queue')


while True:
    task = wordSplit_queue.brpop()
    try:
        str_name = task[1].decode("UTF-8")
        seg_list = jieba.cut(str_name)
        seg_str = ','.join(seg_list)
        session = mkSessions()
        news_words = NewsWords(name=seg_str)
        session.add(news_words)
        session.commit()

        logger.info('分词完成：'+str(len(seg_list)))

    except Exception as e:
        logger.error('Error: '+task+' Handle failed: '+e)