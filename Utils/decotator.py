import functools
import asyncio
from Utils.jwtSign import decode_auth_token
from Utils.logs import logger


def authenticated(func):
    """
    用户Authorization验证装饰器
    """
    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        # 获取 Authorization 请求头
        auth_header = self.request.headers.get('Authorization', None)
        if not auth_header or not auth_header.startswith('Bearer '):
            self.set_status(401)
            self.write({'error': 'Missing or invalid Authorization header'})
            return
        # 提取令牌
        token = auth_header.split(' ')[1]

        try:
            payload = await decode_auth_token(auth_token=token)
            self.current_user = payload['data']  # 提取用户信息
        except Exception as e:
            logger.error(f"用户信息验证错误: {e}")
            self.set_status(401)
            self.write({'error': 'Token has expired'})
            return

        # 验证函数类型，继续执行处理方法
        if asyncio.iscoroutinefunction(func):
            re_func = await func(self, *args, **kwargs)
        else:
            re_func = func(self, *args, **kwargs)
        return re_func
    return wrapper
