#!/usr/bin/python
# coding=utf8

import tornado.web
import tornado.gen
from spider.register import Sp
from tornado.concurrent import run_on_executor
from handler import executor
from Utils.Utils import get_arguments
from db.mysql import sessions
from models.products import ParseLog
from Utils.logs import logger


class crawler_handler(tornado.web.RequestHandler):

    executor = executor

    @tornado.gen.coroutine
    def get(self):
        params = get_arguments(self)
        data = yield self.crawler_parser(params)
        self.record_log(data=data, params=params)
        self.set_header('Content-type', 'application/json')
        self.write(data)

    @run_on_executor
    def crawler_parser(self, params):
        return Sp.parser(params)

    @run_on_executor
    def record_log(self, data, params):
        if data['code'] == 0:
            try:
                data = data['data']
                fluency = data[list(data.keys())[0]]
                name = fluency['name'][0:20]  # 防止有的视频歌曲名字太长，截取前20个字符
                session = sessions()
                parse_log = session.query(ParseLog).filter_by(name=name, pdt_type=params['parseType']).first()
                if parse_log and parse_log.name:
                    session.query(ParseLog).filter_by(name=name, pdt_type=params['parseType']).update({ParseLog.info_num:ParseLog.info_num +1})
                else:
                    parse_log = ParseLog(name=name, pdt_type=params['parseType'], info_num=1)
                    session.add(parse_log)
                session.commit()
            except Exception as e:
                logger.error('Insert record info error: %s: %s' % (params['url'], e))
