#!/usr/bin/python
# coding=utf8

import tornado.web
import tornado.gen
from spider.register import Sp
from tornado.concurrent import run_on_executor
from handler import executor
from Utils.Utils import get_arguments
from db.mysql import sessions
from models.products import ParseLog, ReqUrlNameMapping
from Utils.logs import logger
from Utils.Utils import has_field
import json


class HotWebSite_Handler(tornado.web.RequestHandler):
    executor = executor

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header("Access-Control-Allow-Headers", "x-requested-with,authorization,origin,content-type,accept")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, PUT, DELETE, OPTIONS')
        self.set_header('Content-Type', 'application/json; charset=UTF-8')

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()

    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        session = sessions()
        hotWebSite = session.query(ReqUrlNameMapping).all()
        self.write({'hotWebSite': [i.to_json() for i in hotWebSite]})


# class pageRank_handler(tornado.web.RequestHandler):
#
#     executor = executor
#
#     def set_default_headers(self):
#         self.set_header('Access-Control-Allow-Origin', '*')
#         self.set_header("Access-Control-Allow-Headers", "x-requested-with,authorization,origin,content-type,accept")
#         self.set_header('Access-Control-Allow-Methods', 'POST, GET, PUT, DELETE, OPTIONS')
#         self.set_header('Content-Type', 'application/json; charset=UTF-8')
#
#     def options(self, *args, **kwargs):
#         self.set_status(204)
#         self.finish()
#
#     @tornado.gen.coroutine
#     def get(self, *args, **kwargs):
#         rank = yield self.get_parser_rank()
#         self.write(rank)
#
#     @run_on_executor
#     def get_parser_rank(self):
#         data = ParserRank.objects.order_by('-info_num').all().to_json()
#         pdt_type = set([x['pdt_type'] for x in json.loads(data)])
#         return {'type_num': len(pdt_type), 'pdt_type': list(pdt_type), 'data': json.loads(data)}


class crawler_handler(tornado.web.RequestHandler):

    executor = executor

    @tornado.gen.coroutine
    def get(self):
        params = get_arguments(self)
        data = yield self.crawler_parser(params)
        yield self.record_log(data=data, params=params)
        self.set_header('Content-type', 'application/json')
        if params['search'] and params['search'] == '1':
            self.write({'status': 1, 'message': 'ok'})
            return None
        self.write(data)

    @run_on_executor
    def crawler_parser(self, params):
        return Sp.parser(params)

    @run_on_executor
    def record_log(self, data, params):
        if data['code'] == 0:
            try:
                info_key = {}
                data = data['data']
                session = sessions()
                if params['parseType'] != 'news':
                    fluency = data[list(data.keys())[0]]
                    info_key[fluency['name'][0:50]] = fluency['img'] if has_field(fluency, 'img') else ''   # 防止有的视频歌曲名字太长，截取前20个字符
                else:
                    for hot_new in data:
                        info_key[hot_new['title'][0:50]] = hot_new['url']
                for item in info_key.keys():

                    parse_log = session.query(ParseLog).filter_by(name=item, pdt_type=params['parseType']).first()
                    if parse_log and parse_log.name:
                        session.query(ParseLog).filter_by(name=item, pdt_type=params['parseType']).update(
                            {ParseLog.info_num: ParseLog.info_num + 1, ParseLog.req_url: params['url']})
                    else:
                        parse_log = ParseLog(name=item, pdt_type=params['parseType'], info_num=1, url=info_key[item], req_url=params['url'])
                        session.add(parse_log)
                session.commit()
            except Exception as e:
                logger.error('Insert record info error: %s: %s' % (params['url'], e))