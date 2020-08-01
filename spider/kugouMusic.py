import requests
from Utils.Utils import WebSite, find_one_string, format_url
import json
import re
import os
from lxml import etree
from spider.baseSiteParser import BaseSiteParser, ScpMusicParser


class KuGouMusic(BaseSiteParser):

    def __init__(self, webDriver=False):
        self.driver = WebSite(webDriver=webDriver)
        self.musicTopDict = {}
        self.domain = 'kugou.com'
        self.ScpMusicParser = ScpMusicParser()

    def parser(self, url=None):
        self.parse_item(url=url)

    def parse_item(self, url=None):

        """

        :param url: https://www.kugou.com/song/#hash=58C27D1CE869A64E88296B5E34446B37&album_id=38162889
        :param https://wwwapi.kugou.com/yy/index.php?r=play/getdata&hash=58C27D1CE869A64E88296B5E34446B37&album_id=38162889&mid=21ae69e0a12f2991d4f319ba3579434b&platid=4
        :return:
        x
        """

        if url is None:
            return None

        hash = find_one_string(pattern='hash=(.+?)&', content=url)
        album_id = find_one_string(pattern='album_id=(\d+)', content=url)
        if hash and album_id:
            data_url = "https://wwwapi.kugou.com/yy/index.php?"
            data = {
                'r': 'play/getdata',
                'hash': hash,
                'album_id': album_id,
                'mid': '21ae69e0a12f2991d4f319ba3579434b',
                'platid': 4
            }
            data_url = data_url + format_url(data=data)
            content = self.driver.web_fetch2(data_url)
            try:
                result = json.loads(content)
                if result['status'] == 1 and result['data']:
                    result_data = result['data']

                    img = result_data['img']
                    name = result_data['song_name']
                    duration = result_data['timelength']
                    bitrate = result_data['bitrate']
                    play_url = result_data['play_url']
                    size = result_data['filesize']

                    if not play_url:
                        return None

                    self.ScpMusicParser.set_fluency('hd') \
                        .set_name(name or '') \
                        .set_img(img or '') \
                        .set_duration(duration/1000 or 0) \
                        .set_format('mp4') \
                        .set_bitrate(bitrate or 0) \
                        .set_url(play_url) \
                        .set_size(size or 0)

            except Exception as e:
                return None

    def get_result(self):
        return self.ScpMusicParser.get_params()


# kugou = KuGouMusic()
# kugou.parser("https://www.kugou.com/song/#hash=58C27D1CE869A64E88296B5E34446B37&album_id=38162889")
# print (kugou.get_result())
