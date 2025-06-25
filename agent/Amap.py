import json

import httpx
from Utils.logs import logger

from config import get_configuration, read_excel
from Utils.Utils import format_url, sync_get
from tornado.httpclient import AsyncHTTPClient
from datetime import datetime


AMAP_CONFIG = get_configuration(key='amap')
AMAP_ADCODE = read_excel('AMap_adcode_citycode', sheet='sheet1')


async def agent_distribute(all_weather_data: dict = {}):
    live_data = all_weather_data['lives'][0]
    province = live_data.get('province')
    city = live_data.get('city')
    date = datetime.now().strftime('%Y-%m-%d')
    weather = live_data.get('weather')
    temperature = live_data.get('temperature')
    winddirection = live_data.get('winddirection')
    windpower = live_data.get('windpower')
    reporttime = live_data.get('reporttime')
    weather_model = f"""{province}-{city} 的天气情况如下: \n - 日期：{date} \n - 天气现象：{weather} \n - 气温：{temperature} 摄氏度 \n - 风向：{winddirection} 风, 风力：{windpower} \n - 发布时间：{reporttime}"""
    return weather_model


async def search_weather(location: str = '济南市', date: str = None, extensions: str = 'base', output: str = 'JSON'):
    weather_key = AMAP_CONFIG.get('weather_key')
    weather_url = AMAP_CONFIG.get('weather_url')
    adcode = next((item['adcode'] for item in AMAP_ADCODE if location in item['name']), None)
    json_params = {
        'key': weather_key,
        'city': adcode,
        'extensions': extensions,
        'output': output
    }
    params = format_url(json_params)
    try:
        http_client = AsyncHTTPClient()
        response = await http_client.fetch(weather_url+params, validate_cert=False)
        return json.loads(response.body)
    except Exception as e:
        logger.error(f'天气API接口请求超时{e}')
        print(e)

