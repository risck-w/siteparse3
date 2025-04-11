import jwt
import datetime
import settings


async def encode_auth_token(user):
    """
    :param params:
    :return: token
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2),
            'iat': datetime.datetime.utcnow(), # 开始时间
            'iss': 'wang',  # 签名
            'data': {
                'id': user.id,
                'username': user.username,
                'status': user.status
            } # 内容一般存放用户id
        }
        auth_token = jwt.encode(payload=payload, key=settings.secret, algorithm='HS256')
        return auth_token
    except Exception as e:
        raise Exception("Invalid token")


async def decode_auth_token(auth_token):
    return jwt.decode(jwt=auth_token, key=settings.secret, algorithms=['HS256'])