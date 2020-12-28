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


def has_field(params, field):
    """验证字典中的字段是否存在"""

    assert type(params) == dict

    verify = lambda field: True if field in params.keys() else False
    return verify(field)


_ARG_DEFAULT = object()


def get_arguments(self, default=_ARG_DEFAULT, strip=True):
    params = {}
    source = self.request.arguments
    for name in source.keys():
        value = self._get_argument(name, default, source, strip=strip)
        params[name] = value

    return params


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
    def web_fetch2(url, method='GET', headers=None, data=None, cookies=None, allow_redirects=True):
        # 采用常规requests请求
        if allow_redirects is False:
            return requests.head(url, headers=headers, cookies=cookies, allow_redirects=allow_redirects)
        if method == 'GET':
            return requests.get(url, headers=headers, cookies=cookies, allow_redirects=allow_redirects).text
        return requests.post(url, headers=headers, data=data, cookies=cookies, allow_redirects=allow_redirects).text

    def close(self):
        if self.webDriver is True:
            self.driver.close()

if __name__ == "__main__":
   download('test') 
