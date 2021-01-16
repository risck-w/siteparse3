from abc import ABCMeta, abstractmethod
from Utils.Utils import has_field


class BaseMusicParser(object):

    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def parser(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_result(self):
        pass


class BaseVodParser(object):

    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def parser(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_result(self):
        pass


class BaseLiveParser(object):

    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def parser(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_result(self):
        pass


class BaseNewsParser(object):

    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def parser(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_result(self):
        pass


""" 静态新闻资源数据结构
    :param news: list [{
        title: String 题目，
        description: String 描述，
        images: String 图片地址，
        url：String 详情页地址
    }]

"""


class Begin(object):
    def __init__(self, outer_instance):
        self.single_new = {}
        self.outer_instance = outer_instance

    def set_title(self, title):
        self.single_new['title'] = title
        return self

    def set_description(self, description):
        self.single_new['description'] = description or None
        return self

    def set_images(self, images):
        self.single_new['images'] = images or None
        return self

    def set_url(self, url):
        self.single_new['url'] = url
        return self

    def End(self):
        self.outer_instance.news.append(self.single_new)
        return self.outer_instance


class ScpNewsParser(object):
    def __init__(self):
        self.news = []

    def Begin(self):
        return Begin(self)

    def get_field(self, field=None):
        if not field:
            raise Exception("KeyError: '" + field + "' must be set")
        elif len(self.news) > 0:
            items = []
            for news_field in self.news:
                if has_field(news_field, field):
                    items.append(news_field[field])
            return items
        else:
            raise Exception("KeyError: '" + field + "' must be set")

    def get_params(self):
        return self.news






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


class ScpParser(object):

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