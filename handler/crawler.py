#!/usr/bin/python
# coding=utf8

import tornado.web
import tornado.gen
from spider.register import Sp
from tornado.concurrent import run_on_executor
from handler import executor
from Utils.Utils import get_arguments, async_get_arguments
from db.mysql import sessions
from models.products import ParseLog, ReqUrlNameMapping, HotWords
from Utils.logs import logger
from Utils.Utils import has_field, async_has_field
from db.redis import CreateQueue
import json
import math
import os
from volcenginesdkarkruntime import Ark

from tasks import hello
from celery.result import AsyncResult

client = Ark(
    api_key=os.environ.get('DOUBAO_ARK_API_KEY')
)


class AI_Agent_search_handler(tornado.web.RequestHandler):

    def on_finish(self):
        return super().on_finish()


    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header("Access-Control-Allow-Headers", "x-requested-with,authorization,origin,content-type,accept")
        self.set_header('Access-Control-Allow-Methods', 'GET POST')
        self.set_header('Content-Type', 'text/event-stream; charset=utf-8')
        # 不使用缓存
        self.set_header('Content-Control', "no-cache")
        # 保持长连接
        self.set_header('Connection', "keep-alive")
        self.set_header('X-Accel-Buffering', 'no')
        # 禁用 Tornado 的自动压缩（SSE 不支持压缩）
        self.set_header("Content-Encoding", "identity")

    async def get(self):
        params = await async_get_arguments(self)
        field_valid = await async_has_field(params, 'parseType')
        if field_valid and params['parseType'] == 'AIcontent':
            if 'url' in params and params['url'] is not None:
                stream = client.chat.completions.create(
                    model='ep-20250102154256-z69t4',
                    messages=[
                        {'role': 'user', 'content': params['url']}
                    ],
                    extra_headers={'x-is-encrypted': 'true'},
                    stream=True
                )
                # print(completion.choices[0].message.content)
                for chunk in stream:
                    if not chunk.choices:
                        continue
                    self.write(chunk.choices[0].delta.content + '\n')
                    await self.flush()
                return None
        self.write({'code': '1', 'message': '请正确配置参数'})

    async def post(self, *args, **kwargs):
        url = json.loads(self.request.body)['url']
        parseType = json.loads(self.request.body)['parseType']
        try:
            if parseType == 'AIcontent' and url is not None:
                stream = client.chat.completions.create(
                    model='ep-20250102154256-z69t4',
                    messages=[
                        {'role': 'user', 'content': url}
                    ],
                    extra_headers={'x-is-encrypted': 'true'},
                    stream=True
                )
                # print(completion.choices[0].message.content)
                for chunk in stream:
                    if not chunk.choices:
                        continue
                    print(chunk.choices[0].delta.content)
                    self.write(f'event:answer\ndata: ' + json.dumps({"message": chunk.choices[0].delta.content}) + f'\n\n')
                    await self.flush()
            else:
                self.write({'code': '1', 'message': '请正确配置参数'})
        except tornado.iostream.StreamClosedError:
            print('client disconnected')
        finally:
            self.finish()


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

        # 搜索词云中的关键词新闻
        sql = '''
            select a.name title,b.name res_name, a.url, a.req_url, orig_createtime as updated_dt, date_format(a.udt, '%Y-%m-%d %H:%i:%s') as udt from (
                select name, req_url, url, orig_createtime, created_dt as udt from parse_log where pdt_type = 'news' and name like "%{0}%"
            ) a
            left join req_url_name_mapping b
            on a.req_url = b.url
        '''.format(params['url'])

        if has_field(params, 'parseType') and params['parseType'] == 'website':
            sql = '''
                select a.name title,b.name res_name, a.url, a.req_url, orig_createtime as updated_dt, date_format(a.udt, '%Y-%m-%d %H:%i:%s') as udt from (
                    select name, req_url, url, orig_createtime, created_dt as udt from parse_log where pdt_type = 'news'
                ) a
                left join req_url_name_mapping b
                on a.req_url = b.url
                where  b.name like "%{0}%"
            '''.format(params['url'])

        try:
            session = sessions()
            result = session.execute(sql)
            data = [dict(x.items()) for x in result.fetchall()]
            data.sort(key=lambda x:x['udt'], reverse=True)
            session.close()
            self.write({'code': 0, 'data': data})
        except Exception as e:
            logger.error(e)
            self.write({'code': 1, 'data': None, 'message': 'search error!'})

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


class Hello_handler(tornado.web.RequestHandler):

    async def get(self, *args, **kwargs):
        msg = hello.hello.delay(2, 3)
        """AsyncResult.get方法会阻塞任务的异步执行
        所以得出结论：Celery的使用局限于无返回结果要求的业务场景
        """
        result = AsyncResult(msg).get(timeout=10)  # seconds
        if result is not None:
            self.write({'code': 0, 'msg': result})
        else:
            self.write({'code': 1, 'msg': 'No result'})


class Noblock_handler(tornado.web.RequestHandler):
    async def get(self, *args, **kwargs):
        self.write({'code': 0, 'msg': 0})