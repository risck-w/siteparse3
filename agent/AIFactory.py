import asyncio
from asyncio import Queue
import json
import multiprocessing

import tornado.gen

from agent.client import DoubaoClient, BaseClient
from Utils.Utils import get_uuid
from db.redis import redis
from config import get_prompt
from config import get_configuration
from Utils.logs import logger
from datetime import datetime

client_map = {
    'doubao': DoubaoClient
}



class Conversation(object):

    """上下文会话管理类"""
    def __init__(self, conversation_id: str = None,
                 module: str = None,
                 prompt: str = 'intention',
                 enable_history: bool = False,
                 max_history_num: int = 10,
                 history_expire: int = 600
                 ):
        """
        :param conversation_id (str): 会话id，默认为16位ID
        :param module (str): 会话模型，默认为None
        :param prompt (str): role:user prompt，默认为intention
        :param enable_history (bool): 是否开启上下文对话，默认False
        :param max_history_num (int): 上下文对话最大记录条数，默认10条，仅当enable_history=True时起作用
        :param history_expire (int): 上下文对话过期时间，默认600s，仅当enable_history=True时起作用
        :param sys_prompt (dict): role: system prompt, 根据prompt的值选择不同的系统提示prompt
        :param current_message (str): 在调用build_messages函数时，记录最新一条用户对话内容，默认为None
        :param user_messages_params (dict): 用户role信息
        :return: conversation list
        """
        self.msg_list = []
        self.conversation_id = conversation_id or get_uuid()
        self.prompt = prompt
        self.enable_history = enable_history
        self.max_history_num = max_history_num
        self.history_expire = history_expire
        self.agents_configuration = get_configuration(module)
        self.sys_prompt = {}
        self.current_message = None
        self.user_messages_params = {"role": "user", "content": None}

    def build_messages(self, message: str, intent_prompt: bool = False):
        """
        记录用户信息
        :param message: 用户当前提问内容
        :return: list
        """
        self.current_message = message
        if intent_prompt:
            pre_prompt = get_prompt('pre_prompt')
            message = pre_prompt.format(message=message)
        self.user_messages_params['content'] = message
        self.sys_prompt = {"role": "system", "content": get_prompt(self.prompt)}
        if self.enable_history:
            msg_history_data = redis.get(self.conversation_id)
            if msg_history_data:
                self.msg_list = json.loads(msg_history_data)
            self.msg_list.append(self.user_messages_params)
            self.msg_list = [self.sys_prompt] + self.msg_list[1:][-int(self.max_history_num):]
            redis.set(self.conversation_id, json.dumps(self.msg_list), ex=self.history_expire)
        else:
            self.msg_list.append(self.sys_prompt)
            self.msg_list.append(self.user_messages_params)

        self.agents_configuration['conversation_id'] = self.conversation_id
        self.agents_configuration['conversation'] = self.msg_list
        self.agents_configuration['prompt'] = self.sys_prompt
        self.agents_configuration['extra_headers'] = {'x-is-encrypted': 'true'}
        return self.conversation_id, self.agents_configuration

    def reset_prompt(self, prompt: str = 'agi_prompt'):
        # 清理redis当前会话
        redis.delete(self.conversation_id)
        # 初始化用户内容上下文
        self.msg_list = []
        # 初始化系统prompt
        self.sys_prompt['content'] = get_prompt(prompt)
        self.msg_list.append(self.sys_prompt)
        # 初始化用户prompt
        self.user_messages_params['content'] = self.current_message
        self.msg_list.append(self.user_messages_params)
        # 初始化模型角色类型
        self.prompt = self.msg_list[-1]
        # 初始化agent配置参数
        self.agents_configuration['prompt'] = self.sys_prompt
        self.agents_configuration['conversation'] = self.msg_list
        return self.conversation_id, self.agents_configuration


def call_agent(client: BaseClient, configuration: dict = {}, stream: bool = False, queue: Queue = None):
    """
    在子进程中调用OpenAI SDK
    :param client: 模型类
    :param configuration: 配置参数
    :param stream: 输出结果类型
    :param queue: 当前对话的队列实例
    :return: completion, 模型返回数据放入队列
    """
    try:
        agent_client = client(
            api_key=configuration.get('api_key'),
            base_url=configuration.get('base_url'),
            model=configuration.get('model')
        )
        completion = agent_client.chat_completion(
            conversation=configuration.get('conversation'),
            stream=stream,
            extra_headers=configuration.get('extra_headers')
        )
        if stream:
            for chunk in completion:
                queue.put(chunk.choices[0].delta.content)
        else:
            queue.put(completion.choices[0].message.content)
    except Exception as e:
        queue.put_nowait({"error": f"call_agent {str(e)}"})
    finally:
        # 发送结束信号
        queue.put_nowait(None)


def _call_agent(client: BaseClient, configuration: dict = {}, stream: bool = False):
    """
    调用OpenAI SDK
    :param client: 模型类
    :param configuration: 配置参数
    :param stream: 输出结果类型
    :return: completion, 模型返回数据
    """
    try:
        agent_client = client(
            api_key=configuration.get('api_key'),
            base_url=configuration.get('base_url'),
            model=configuration.get('model')
        )
        completion = agent_client.chat_completion(
            conversation=configuration.get('conversation'),
            stream=stream,
            extra_headers=configuration.get('extra_headers')
        )
        return completion
    except Exception as e:
        print(e)
        return {"error": str(e)}


async def run_in_pool(client: BaseClient, configuration: dict = {}, stream: bool = False) -> asyncio.Queue:
    """
    在进程池中运行call_agent任务函数, 并为每一个请求动态创建分配一个唯一的对列
    :param client: 模型类
    :param configuration: 配置参数
    :param stream: 输出结果类型
    :return: Queue 返回队列实例
    """

    loop = asyncio.get_event_loop()
    manager = multiprocessing.Manager()
    queue = manager.Queue()

    try:
        with multiprocessing.Pool(1) as pool:
            await loop.run_in_executor(None, pool.apply, call_agent, (client, configuration, stream, queue))
            return manager, queue
    except Exception as e:
        print(e)
        return {"error": str(e)}


async def build_agent(configuration: dict, stream: bool = False):
    agent_name = configuration.get('agent_name')
    if agent_name not in client_map.keys():
        raise Exception('agent name 不存在')
    agent_client = client_map[agent_name]
    logger.info(f"用户调用模型：{agent_name}, 配置获取完成, 开始处理任务")
    logger.info(configuration["conversation"])
    manager, queue = await run_in_pool(agent_client, configuration, stream)
    logger.info(f"用户调用模型：{agent_name}, 任务处理完成")
    return manager, queue

