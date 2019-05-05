import re
import createDriver
from urllib import request


def find_one_string(pattern, content, flags=0):
    if pattern is None or content is None:
        return None
    patterns = re.compile(pattern=pattern, flags=flags)
    try:
        return patterns.search(content).group(1)
    except AttributeError:
        return None


class Util(object):
    def __init__(self, webDriver=False):
        # 获取浏览器对象
        self.webDriver = webDriver
        self.driver = None
        if webDriver is True:
            self.driver = self.create_driver()
        else:
            self.driver = request

    def create_driver(self):
        if self.driver:
            return self.driver
        if self.webDriver is True:
            return createDriver.CreateWebDriver().get_driver
        return request

    def web_fetch(self, url, headers={}):
        # 打开浏览器驱动
        if self.webDriver is True:
            self.driver.get(url=url)
            return self.driver.page_source

        # 采用常规request请求
        req = self.driver.Request(url=url)
        if headers:
            for key in headers:
                req.add_header(key=key, headers=headers[key])
        return self.driver.urlopen(req).read().decode('utf-8')

    def web_fetch2(self, url, headers={}):
        # 采用常规request请求
        req = request.Request(url=url)
        if headers:
            for key in headers:
                req.add_header(key=key, val=headers[key])
        return request.urlopen(req).read().decode('utf-8')

    def close(self):
        if self.webDriver is True:
            self.driver.close()
