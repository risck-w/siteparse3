from spider.baseSiteParser import BaseSiteParser, ScpParser
from Utils.Utils import find_one_string, WebSite


class Douyin(BaseSiteParser):

    def __init__(self):
        self.domain = 'douyin.com'  # 初始化网站域名
        self.ScpParser = ScpParser()  # 初始化实例类
        self.params = {}

    def parser(self, url):
        if url:
            headers = {
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36'
            }
            self.params['content'] = WebSite.web_fetch2(url=url, headers=headers)
        videoUrl = find_one_string(pattern='playAddr:[\s]*?\"(.+)\",', content=self.params['content'])
        videoUrl = videoUrl.replace('playwm', 'play')
        self.ScpParser.set_vod_video(url=videoUrl)

    def get_result(self):
        return self.ScpParser.get_params()
