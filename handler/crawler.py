#!/usr/bin/python
# coding=utf8

import tornado.web
import tornado.gen
import tornado.ioloop
import asyncio
from spider.register import Sp
from tornado.concurrent import run_on_executor
from handler import executor
from Utils.Utils import get_arguments, async_get_arguments
from db.mysql import sessions
from models.products import ParseLog, ReqUrlNameMapping, HotWords
from Utils.logs import logger
from Utils.Utils import has_field, async_has_field
from Utils.decotator import authenticated
from db.redis import CreateQueue
import json
import math
from tasks import hello
from celery.result import AsyncResult

from config import get_configuration
from agent.AIFactory import build_agent, Conversation
from agent.Amap import search_weather, agent_distribute


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
        self.set_header('Cache-Control', "no-cache")
        # 保持长连接
        self.set_header('Connection', "keep-alive")
        self.set_header('X-Accel-Buffering', 'no')
        # 禁用 Tornado 的自动压缩（SSE 不支持压缩）
        self.set_header("Content-Encoding", "identity")

    async def get(self):
        self.set_status(400)
        self.finish()

    @authenticated
    async def post(self, *args, **kwargs):
        url = json.loads(self.request.body)['url']
        parse_type = json.loads(self.request.body)['parseType']
        conversation_id = json.loads(self.request.body)['conversation_id']
        user_id = self.current_user['id']
        stream = False
        try:
            if parse_type == 'AIcontent' and url is not None:
                # 理解用户意图
                conversation = Conversation(conversation_id=conversation_id, module='doubao', prompt='intention', enable_history=True)
                conversation_id, cov_configuration = conversation.build_messages(message=str(url), intent_prompt=True)
                manager_q, completion = await build_agent(configuration=cov_configuration, stream=stream)
                intent_content = None
                while True:
                    chunk = completion.get()
                    if chunk is None:
                        manager_q.shutdown()
                        break
                    if isinstance(chunk, dict) and "error" in chunk:
                        # 如果是dict类型，则是错误信息，发送错误并结束请求
                        self.write(f'event:answer\ndata: ' + json.dumps({"id": conversation_id, "message": '未理解您的意思，您可以把问题描述的再详细一点~'}) + f'\n\n')
                        await self.flush()
                        manager_q.shutdown()
                        break
                    intent_content = chunk

                logger.info(f"用户意图：{intent_content}")
                intent_content = json.loads(intent_content)
                user_intent = intent_content.get('user_intent')
                if user_intent and user_intent == '查询天气':
                    city = intent_content['data']['location']
                    date = intent_content['data']['date']
                    if city:
                        all_weather_data = await search_weather(location=city)
                        weather_model = await agent_distribute(all_weather_data)
                        self.write(f'event:answer\ndata: '
                                   + json.dumps({"id": conversation_id, "message": weather_model})
                                   + f'\n\n')
                        await self.flush()
                    else:
                        self.write(f'event:answer\ndata: '
                                   + json.dumps({"id": conversation_id, "message": '请告知我待查询天气的城市~'})
                                   + f'\n\n')
                        await self.flush()
                else:
                    logger.info(f"调用模型：根据用户意图，重新回答用户问题")
                    stream = True
                    conversation = Conversation(conversation_id=conversation_id, module='doubao', prompt='agi', enable_history=False)
                    conversation_id, cov_configuration = conversation.build_messages(message=str(url), intent_prompt=False)
                    manager_q, completion = await build_agent(configuration=cov_configuration, stream=stream)
                    if stream:
                        while True:
                            chunk = completion.get()
                            if chunk is None:
                                manager_q.shutdown()
                                break
                            if isinstance(chunk, dict) and "error" in chunk:
                                # 如果是dict类型，则是错误信息，发送错误并结束请求
                                self.write(f'event:answer\ndata: ' + json.dumps(
                                    {"id": conversation_id, "message": '未理解您的意思，您可以把问题描述的再详细一点~'}) + f'\n\n')
                                await self.flush()
                                manager_q.shutdown()
                                break
                            self.write(f'event:answer\ndata: '
                                       + json.dumps({"id": conversation_id, "message": chunk})
                                       + f'\n\n')
                            await self.flush()
                        self.write(f"event:answer\ndata: "
                                       + json.dumps({"id": conversation_id, 'message': '[DONE]'})
                                       + f"\n\n")
                        await self.flush()
                    else:
                        self.write({"id": conversation_id, "message": completion})
                manager_q.shutdown()
            else:
                self.write({'code': '1', 'message': '请正确配置参数'})
        except Exception as e:
            self.set_status(500)
            self.write({"error": str(e)})
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