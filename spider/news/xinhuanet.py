from ..baseSiteParser import BaseNewsParser, ScpNewsParser
from Utils.Utils import WebSite, find_one_string
from bs4 import BeautifulSoup
import json


class XinhuanetParser(BaseNewsParser):

    def __init__(self):
        self.domain = 'xinhuanet.com'
        self.ScpNewsParser = ScpNewsParser()

    def parser(self, url):

        # top: http://www.news.cn/json/bangdan/top1.json
        # list：http://www.news.cn/json/bangdan/2021-1/3/a800a274f25141d6b720280a77f12d68.json?callback=xinhuaHotList&_=1609674180652

        top_url = 'http://www.news.cn/json/bangdan/top1.json'
        content = WebSite.web_fetch2(top_url)
        content = find_one_string(pattern='var top1=(.*)', content=content)
        json_content = json.loads(content)
        hot_news_list = json_content['list']
        if len(hot_news_list):
            for news in hot_news_list:
                url = news['subpath']
                if not url:
                    continue
                news_content = WebSite.web_fetch2(url)
                news_info = find_one_string(pattern='xinhuaHotList\((.*)\)' , content=news_content)
                _news_info = json.loads(news_info)['list'][0]

                description = _news_info['contentAbstract']
                title = _news_info['contentTitle']
                news_url = _news_info['contentUrl']

                seq = self.ScpNewsParser.Begin()


                images_url = None
                if 'imageList' in _news_info:
                    try:
                        images_url = _news_info['imageList'][0]['imageUrl']
                    except Exception as e:
                        pass

                seq.set_url(news_url) \
                    .set_title(title) \
                    .set_description(description)

                if images_url:
                    seq.set_images(images_url)

                seq.End()

    def get_result(self):
        return self.ScpNewsParser.get_params()