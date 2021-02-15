#!/usr/bin/python
# coding=utf8

import tornado.web
import tornado.gen
from spider.register import Sp
from tornado.concurrent import run_on_executor
from handler import executor
from Utils.Utils import get_arguments
from db.mysql import sessions
from models.products import ParseLog, ReqUrlNameMapping, HotWords
from Utils.logs import logger
from Utils.Utils import has_field
from db.redis import CreateQueue
from sqlalchemy.sql import func
import json
import math
import time


class Top_HotWebSite_Handler(tornado.web.RequestHandler):
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
        sql = '''
            select d.name, c.count, d.color from (
                select count(b.info_num) count , b.req_url from (
                 select * from parse_log a where a.pdt_type = 'news'
                ) b
                group by b.req_url
            ) c
            left join req_url_name_mapping d
            on c.req_url = d.url
        '''
        orig_data = session.execute(sql)
        sumHotWebSite = [dict(x.items()) for x in orig_data.fetchall()]
        sumHotWebSite.sort(key=lambda x:x['count'], reverse=True)
        if len(sumHotWebSite) > 8:
            sumHotWebSite = sumHotWebSite[:8]
        session.close()

        self.write({'topHotWebSite': sumHotWebSite})


class WordCloud_Handler(tornado.web.RequestHandler):
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
        word_cloud = session.query(HotWords).all()
        # data = [i.to_json() for i in word_cloud]
        session.close()
        trans_data = []
        for i in word_cloud:
            temp = {}
            temp['name'] = i.word
            temp['value'] = i.num
            temp['updated_dt'] = str(i.update_dt)
            trans_data.append(temp)
        trans_data.sort(key=lambda item: item['value'], reverse=True)
        rindex = len(trans_data)
        if rindex >= 100:
            rindex = int(math.ceil(len(trans_data)/10))
        self.write({'wordCloud': trans_data[:rindex]})


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
        session.close()
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
        self.set_header('Content-type', 'application/json')
        if 'search' in params and params['search'] == '1':
            data = Sp.isCheck(params=params)
            try:
                if data['code'] == 0:
                    crawler_queue = CreateQueue('crawlerQueue')
                    crawler_queue.lpush(json.dumps(params))
                    self.write({'status': 0, 'message': 'ok'})
                else:
                    self.write({'status': 1, 'message': '暂不支持解析'})
                return None
            except Exception as e:
                logger.error(e)
        data = yield self.crawler_parser(params)
        self.record_log(data=data, params=params)
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
                session.close()
            except Exception as e:
                logger.error('Insert record info error: %s: %s' % (params['url'], e))