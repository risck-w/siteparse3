import json
from spider.baseSiteParser import BaseVodParser, ScpParser
from Utils.Utils import find_one_string, WebSite
from Utils.Utils import format_url



class Douyin(BaseVodParser):

    def __init__(self):
        self.domain = 'douyin.com'  # 初始化网站域名
        self.ScpParser = ScpParser()  # 初始化实例类
        self.params = {}

    def parser(self, url):

        # https://v.douyin.com/J6e6ovQ/  -- 阻断304获取 location
        # 从location 中获取item_ids
        # https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids=6857050432208948483&dytk=
        res = WebSite.web_fetch2(url=url, allow_redirects=False)
        location = res.headers['location']
        self.parse_item(location)

    def parse_item(self, url):
        if not url:
            return None

        item_ids = find_one_string('share/video/(.+?)/', content=url)
        if not item_ids:
            return None

        params = {
            'item_ids': item_ids,
            'dytk': ''
        }
        data_url = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?' + format_url(params)
        content = WebSite.web_fetch2(data_url)
        _data = json.loads(content)
        if _data and _data['status_code'] == 0 and _data['item_list']:
            video = _data['item_list'][0]['video']
            video_url = video['play_addr']['url_list'][0]
            duration = video['duration']
            img = video['cover']['url_list'][0]
            bit_rate = video['bit_rate']
            title = _data['item_list'][0]['desc']
            height = video['height']
            width = video['width']

            self.ScpParser.set_fluency('hd') \
                .set_format('mp4') \
                .set_duration(duration/1000) \
                .set_bitrate(bit_rate) \
                .set_img(img) \
                .set_url(video_url) \
                .set_name(title) \
                .set_height(height) \
                .set_width(width)

    def get_result(self):
        return self.ScpParser.get_params()
