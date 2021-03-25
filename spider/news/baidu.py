from spider.baseSiteParser import BaseNewsParser, ScpNewsParser
from Utils.Utils import find_one_string, WebSite
from bs4 import BeautifulSoup


class BaiduParser(BaseNewsParser):
    def __init__(self):
        self.domain = 'baidu.com'
        self.ScpNewsParser = ScpNewsParser()

    def parser(self, url):
        if not url:
            return None

        content = WebSite.web_fetch2(url)
        soup = BeautifulSoup(content, "lxml")
        pane_news = soup.find(id="pane-news")
        hot_news = pane_news.find_all(target="_blank")
        for news in hot_news:
            url = news.get('href')
            title = news.string or (news.contents[0] if len(news.contents) > 0 else None)
            self.ScpNewsParser.Begin()\
                .set_title(title)\
                .set_url(url)\
                .End()

    def get_result(self):
        return self.ScpNewsParser.get_params()

