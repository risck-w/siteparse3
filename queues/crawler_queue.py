import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))

import json
import logging
from Utils.Utils import has_field, getCurrentTime
from spider.register import Sp
from models.products import ParseLog
from db.mysql import sessions
from db.redis import redis, CreateQueue
from scripts.crontabs.wordSplitToMysql import sync_data


logger = logging.getLogger(__name__)

crawler_queue = CreateQueue('crawlerQueue')


def crawler_parser(params):
    return Sp.parser(params)


def record_log(data, params):
    if data['code'] == 0:
        try:
            info_key = {}
            createTime_key = {}
            data = data['data']
            session = sessions()
            if params['parseType'] != 'news':
                fluency = data[list(data.keys())[0]]
                info_key[fluency['name'][0:50]] = fluency['img'] if has_field(fluency,
                                                                              'img') else ''  # 防止有的视频歌曲名字太长，截取前20个字符
            else:
                for hot_new in data:
                    info_key[hot_new['title'][0:50]] = hot_new['url']
                    if has_field(hot_new, 'orig_createtime'):
                        createTime_key[hot_new['title'][0:50]] = hot_new['orig_createtime']
                    else:
                        createTime_key[hot_new['title'][0:50]] = str(getCurrentTime())
            for item in info_key.keys():

                parse_log = session.query(ParseLog).filter_by(name=item, pdt_type=params['parseType']).first()
                if parse_log and parse_log.name:
                    session.query(ParseLog).filter_by(name=item, pdt_type=params['parseType']).update(
                        {ParseLog.info_num: ParseLog.info_num + 1, ParseLog.req_url: params['url'], ParseLog.orig_createtime:createTime_key[item], ParseLog.updated_dt: getCurrentTime()})
                else:
                    parse_log = ParseLog(name=item, pdt_type=params['parseType'], info_num=1, url=info_key[item],
                                         req_url=params['url'], orig_createtime=createTime_key[item],updated_dt=getCurrentTime(), created_dt=getCurrentTime())
                    session.add(parse_log)
            session.commit()
            sessions.close()

        except Exception as e:
            logger.error('Insert record info error: %s: %s' % (params['url'], e))


while True:
    task = crawler_queue.brpop()
    try:
        task = json.loads(task[1].decode("UTF-8"))
        data = crawler_parser(task)
        record_log(data, task)
        logger.info(task['url']+' Handle successful')
        sync_data()
    except Exception as e:
        logger.error('Error: '+task+' Handle failed: '+e)






