from abc import ABCMeta, abstractmethod


class BaseSiteParser(object):

    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def parser(self):
        pass

    @abstractmethod
    def get_result(self):
        pass


class ScpParser(object):

    def __init__(self):
        self.params = {'code': 0,
                       'author': 'risck-w',
                       'vod': {'music': [], 'video': []},
                       'live': {'video': []},
                       'content': []}

    def set_vod_music(self, url=None):
        self.params['vod']['music'].append(url)

    def get_vod_music(self):
        try:
            return self.params['vod']['music']
        except Exception as e:
            return []

    def set_vod_video(self, url=None):
        self.params['vod']['video'].append(url)

    def get_vod_video(self):
        try:
            return self.params['vod']['video']
        except Exception as e:
            return []

    def set_content(self, content=None):
        self.params['content'].append(content)

    def get_content(self):
        try:
            return self.params['content']
        except Exception as e:
            return []

    def set_headers(self, header={}):
        self.params['headers'] = header

    def get_headers(self):
        try:
            return self.params['headers']
        except Exception as e:
            return {}

    def get_params(self):
        return self.params