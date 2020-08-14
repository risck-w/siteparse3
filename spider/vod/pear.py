import re
from Utils.Utils import find_one_string, WebSite
from spider.baseSiteParser import BaseVodParser, ScpParser


class PearVideo(BaseVodParser):

    def __init__(self):
        self.domain = 'pearvideo.com'
        self.ScpParser = ScpParser()

    def parser(self, url):
        if not url:
            return None

        content = WebSite.web_fetch2(url)
        play_url = find_one_string('srcUrl=\"(.+?)\"', content)
        img = find_one_string('<img class=\"img\" src=\"(.+?)\"', content, re.M)
        name = find_one_string('<title>(.+?)</title>', content)

        self.ScpParser.set_fluency('hd') \
            .set_url(play_url) \
            .set_name(name) \
            .set_img(img) \
            .set_format(self.get_video_type(url))

    def get_video_type(self, url):
        if '.flv' in url:
            return 'flv'
        return 'mp4'

    def get_result(self):
        return self.ScpParser.get_params()