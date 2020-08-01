import re
import os
import requests
from Utils import createDriver
from urllib import request
from urllib.parse import unquote


def download(url, songName, headers={}):
    req_headers = None
    if len(headers) > 0:
        req_headers = headers
    music = requests.get(url, headers)
    parent_path = os.path.abspath('.')
    song_url = parent_path + '/' + songName
    with open(song_url, 'wb') as m:
        m.write(music.content)


def format_url(data={}):
    """

    :param data: URL(Method: GET) params dict
    :return: String
    """
    format_str = ''
    if data:
        for key in data.keys():
            format_str = format_str + '&' + key + '=' + str(data[key])
    return format_str


def find_domain(url):
    pattern = r"http[s]*://[a-z0-9]+\.([a-z0-9]+(-[a-z0-9]+)*\.+[a-z]{2,}\b)"
    domain = find_one_string(pattern=pattern, content=unquote(url))
    if not domain:
        return find_one_string(pattern=pattern, content=unquote(url))
    return domain


def find_one_string(pattern, content, flags=0):
    if pattern is None or content is None:
        return None
    try:
        patterns = re.compile(pattern=pattern, flags=flags)
        return patterns.search(content).group(1)
    except AttributeError:
        return None


class WebSite(object):
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

    @staticmethod
    def web_fetch2(url, headers={}, data=None, allow_redirect=True):
        # 采用常规request请求
        req = request.Request(url=url, data=data)
        if headers:
            for key in headers:
                req.add_header(key=key, val=headers[key])
        if not allow_redirect:
            return request.urlopen(req)

        return request.urlopen(req).read().decode('utf-8')

    def close(self):
        if self.webDriver is True:
            self.driver.close()

if __name__ == "__main__":
   download('test') 
