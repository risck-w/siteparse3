import re
import os
import requests
from Utils import createDriver
from urllib import request


def download(url, songName, headers={}):
    req_headers = None
    if len(headers) > 0:
        req_headers = headers
    music = requests.get(url, headers)
    parent_path = os.path.abspath('.')
    song_url = parent_path + '/' + songName
    with open(song_url, 'wb') as m:
        m.write(music.content)


def find_domain(url):
    pattern = r"http[s]*://[a-z0-9]+\.([a-z0-9]+(-[a-z0-9]+)*\.+[a-z]{2,}\b)"
    return find_one_string(pattern=pattern, content=url)


def find_one_string(pattern, content, flags=0):
    if pattern is None or content is None:
        return None
    try:
        patterns = re.compile(pattern=pattern, flags=flags)
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

if __name__ == "__main__":
   download('test') 
