import logging
from bs4 import BeautifulSoup
from Utils.Utils import WebSite
from spider.baseSiteParser import BaseNewsParser, ScpNewsParser


logger = logging.getLogger(__name__)


class RmltParser(BaseNewsParser):

    def __init__(self):
        self.domain = 'rmlt.com.cn'
        self.Scp = ScpNewsParser()

    def parser(self, url):
        logger.info(url)
        content = WebSite.web_fetch2(url, decode='utf-8')
        soup = BeautifulSoup(content, 'lxml')
        fgxnews = soup.find_all('li', class_='fgxnews')
        for tree in fgxnews:
            tag = tree.find('a', target='_blank', title=True)
            title = tag.get('title')
            url = tag.get('href')
            seg = self.Scp.Begin()
            seg.set_title(title) \
                .set_url(url) \
                .End()

    def get_result(self):
        return self.Scp.get_params()
