import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))

import jieba
import string
import json
import hashlib
from Utils.logs import logger
from db.redis import redis, CreateQueue
from db.mysql import sessions as mkSessions
from models.products import NewsWords


logger.info('start parse word split task...')

wordSplit_queue = CreateQueue('wordSplit_queue')
set_queue = CreateQueue('set_queue')


while True:
    task = wordSplit_queue.brpop()
    try:
        data = json.loads(task[1].decode("UTF-8"))
        str_name = data['name']
        url = data['url']

        # 生成hash做对比，没有：插入，有：不做分词
        orig_md5_info = str_name+url
        m = hashlib.md5()
        m.update(orig_md5_info.encode('utf-8'))
        hash_info = m.hexdigest()
        try:
            ismember = set_queue.sismember(hash_info)
            if ismember:
                continue
            set_queue.sadd(hash_info)
        except Exception as e:
            logger.error(e)
            logger.error('connect redis error: set_queue')
            continue

        str_name = str_name.translate(str.maketrans("", "", string.punctuation))
        seg_list = jieba.cut(str_name)
        seg_str = ','.join(seg_list)
        session = mkSessions()
        news_words = NewsWords(name=seg_str)
        session.add(news_words)
        session.commit()
        logger.info('分词完成')

    except Exception as e:
        logger.error('Error: '+task+' Handle failed: '+str(e))