from ..baseSiteParser import BaseNewsParser, ScpNewsParser
from Utils.Utils import WebSite
from bs4 import BeautifulSoup


class DZRBParser(BaseNewsParser):

    def __init__(self):
        self.domain = 'dzng.com'
        self.ScpNewsParser = ScpNewsParser()

    def parser(self, url):
        print(url)
        if not url:
            return None

        content = WebSite.web_fetch2(url)
        soup = BeautifulSoup(content, 'lxml')
        news_list = soup.find(class_='list')
        ul = news_list.ul
        hot_news = ul.find_all('a', target='_blank', title=True)
        for news in hot_news:
            title = news.string or (news.contents[0] if len(news.contents) > 0 else None)
            url = news.get('href')
            if 'http' not in url:
                url = 'https://dzrb.dzng.com' + url # 防止有的链接使用的是相对路径
            self.ScpNewsParser.Begin() \
                .set_title(title) \
                .set_url(url) \
                .End()

    def get_result(self):
        return self.ScpNewsParser.get_params()