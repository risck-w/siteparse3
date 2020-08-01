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
                       'music': [],
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


"""爬虫数据结构
    :param music: Dict {
        key in ('ld' | 'sd' | 'hd') : {
            name: String 歌曲名字,
            img: String 图片地址
            music : {
                bitrate: Integer 码率,
                duration: Integer 时长,
                format: String 格式,
                height: Integer 高度,
                width: Integer 宽度,
                size: Integer 大小,
                play_url: String 音乐地址
            }   
        }
    }
"""


class ScpMusicParser(object):

    def __init__(self):
        self.music = {}
        self.fluency = None
        self.info = 'data'

    def set_fluency(self, fluency='ld'):
        self.fluency = fluency
        self.music[fluency] = {self.info: {}}
        return self

    def set_name(self, name=None):
        if self.fluency is None:
            raise Exception('Error: must be set `fluency` params by `set_fluency` function!')
        self.music[self.fluency]['name'] = name
        return self

    def set_img(self, img=None):
        if self.fluency is None:
            raise Exception('Error: must be set `fluency` params by `set_fluency` function!')
        self.music[self.fluency]['img'] = img
        return self

    def set_url(self, play_url=''):
        if self.fluency is None:
            raise Exception('Error: must be set `fluency` params by `set_fluency` function!')
        self.music[self.fluency][self.info]['play_url'] = play_url
        return self

    def set_bitrate(self, bitrate=0):
        if self.fluency is None:
            raise Exception('Error: must be set `fluency` params by `set_fluency` function!')
        self.music[self.fluency][self.info]['bitrate'] = bitrate
        return self

    def set_duration(self, duration=0):
        if self.fluency is None:
            raise Exception('Error: must be set `fluency` params by `set_fluency` function!')
        self.music[self.fluency][self.info]['duration'] = duration
        return self

    def set_format(self, format=''):
        if self.fluency is None:
            raise Exception('Error: must be set `fluency` params by `set_fluency` function!')
        self.music[self.fluency][self.info]['format'] = format
        return self

    def set_height(self, height=0):
        if self.fluency is None:
            raise Exception('Error: must be set `fluency` params by `set_fluency` function!')
        self.music[self.fluency][self.info]['height'] = height
        return self

    def set_width(self, width=0):
        if self.fluency is None:
            raise Exception('Error: must be set `fluency` params by `set_fluency` function!')
        self.music[self.fluency][self.info]['width'] = width
        return self

    def set_size(self, size=0):
        if self.fluency is None:
            raise Exception('Error: must be set `fluency` params by `set_fluency` function!')
        self.music[self.fluency][self.info]['size'] = size
        return self

    def get_field(self, field=None):
        if not field:
            raise Exception("KeyError: '" + field + "' must be set")
        elif field in self.music.keys():
            return self.music[self.fluency]
        elif field in self.music[self.fluency].keys():
            return self.music[self.fluency][field]
        elif field in self.music[self.fluency][self.info].keys():
            return self.music[self.fluency][self.info][field]
        else:
            raise Exception("KeyError: '" + field + "' must be set")

    def get_params(self):
        return self.music