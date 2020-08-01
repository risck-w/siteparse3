from spider.baseSiteParser import BaseSiteParser, ScpParser
from Utils.Utils import find_one_string, WebSite


class Douyin(BaseSiteParser):

    def __init__(self):
        self.domain = 'douyin.com'  # 初始化网站域名
        self.ScpParser = ScpParser()  # 初始化实例类
        self.params = {}

    def parser(self, url):
        pass

    def get_result(self):
        return self.ScpParser.get_params()
