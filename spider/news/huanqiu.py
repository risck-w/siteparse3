from spider.baseSiteParser import BaseNewsParser, ScpNewsParser
from Utils.logs import logger
from Utils.Utils import WebSite, has_field, getCurrentTime, format_url
from Utils.Utils import get_number_length
from bs4 import BeautifulSoup
import json


class HuanQiuParser(BaseNewsParser):

    def __init__(self):
        self.domain = 'huanqiu.com'
        self.Scp = ScpNewsParser()

    def parser(self, url):
        url = 'https://china.huanqiu.com/api/navigate?type=column&path=http://china.cse3pl8tdbi.huanqiu.com/focus'
        list2_url = 'https://china.huanqiu.com/api/list2?'

        focus = WebSite.web_fetch2(url)
        data = json.loads(focus)

        if has_field(data, 'code'):
            if data['code'] != 200:
                return None

        key_info = data['data']
        catnode = None
        for cla in key_info:
            if 'china.huanqiu.com/focus' == cla['url']:
                catnode = cla['catnode'][0]['catnode']
                break

        params = {
            'node': catnode,
            'offset': 0,
            'limit': 20
        }
        list2_url = list2_url + format_url(params)

        content = WebSite.web_fetch2(list2_url)

        content = json.loads(content)
        if has_field(content, 'list'):
            news = content['list']
            for new in news:
                title = None
                url = None
                try:
                    title = new['title']
                    url = new['source']['url']
                except Exception as e:
                    logger.info(e)
                    continue
                if title is None or title == '':
                    continue

                seg = self.Scp.Begin()

                seg.set_title(title)
                seg.set_url(url)

                if has_field(new, 'summary'):
                    seg.set_description(new['summary'])

                if has_field(new, 'ctime'):
                    seg.set_orig_createtime(str(getCurrentTime(new['ctime'])))

                if has_field(new, 'cover'):
                    cover = new['cover']
                    if cover:
                        if 'http:' not in cover:
                            cover = 'http:' + cover
                    seg.set_images(cover)

                seg.End()

    def get_result(self):
        return self.Scp.get_params()
