import requests
from Utils.Utils import Util, find_one_string
import json
import re
import os
from lxml import etree
from spider.baseSiteParser import BaseSiteParser, ScpParser


class KuGouMusic(BaseSiteParser):

    def __init__(self, webDriver=False):
        self.driver = Util(webDriver=webDriver)
        self.musicTopDict = {}
        self.domain = 'kugou.com'
        self.ScpParser = ScpParser()

    def parser(self, url=None):
        self.parse_item(url=url)

    def parse_item(self, url=None):

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
        }
        self.ScpParser.set_headers(headers)

        # 榜单列表
        url = "https://www.kugou.com/yy/html/rank.html?from=homepage"
        content = self.driver.web_fetch2(url=url)
        if content is None:
            raise Exception("web_fetch Error")
        root = etree.HTML(content)
        music_tree = root.xpath("/html/body/div[3]/div/div[1]/div[1]/ul/li")
        for item_tree in music_tree:
            musci_list_tree = item_tree.xpath("a/@href")
            musci_list_title = item_tree.xpath("a/@title")

            if type(musci_list_title) is not list or musci_list_title is None:
                musci_list_title[0] = "未知榜单"

            if type(musci_list_tree) is list and musci_list_tree:
                if musci_list_title[0] in self.musicTopDict:
                    self.musicTopDict[musci_list_title[0]].append(musci_list_tree)
                    continue
                self.musicTopDict[musci_list_title[0]] = musci_list_tree

        self.parse_music_page()

    def parse_music_page(self):
        if self.musicTopDict is None:
            return

        for key in self.musicTopDict:
            for link in self.musicTopDict[key]:
                content = self.driver.web_fetch2(link)
                if content is None:
                    continue
                # 获取每个榜单的音乐列表
                music_info_dict = find_one_string(pattern="global.features = (\[.+?\]);", content=content)
                self.parse_music_info(music_title=key, info=music_info_dict)
                break
            break

    # 访问音乐播放页面，下载音乐
    def parse_music_info(self, music_title, info):
        info = json.loads(info)
        for item in info:
            music_page_url = "https://wwwapi.kugou.com/yy/index.php?r=play/getdata&callback=&hash={0}&mid={1}".format(item["Hash"], item["album_id"])
            try:
                content = self.driver.web_fetch2(music_page_url)
                music_json_info = json.loads(content)
                if music_json_info["err_code"] == 0 and music_json_info["data"]:
                    music_reall_url = music_json_info["data"]["play_url"]
                    self.ScpParser.set_vod_music(music_reall_url)
                break
            except Exception as e:
                print (e)

    def get_result(self):
        return self.ScpParser.get_params()

# KuGouMusic().parser("https://www.kugou.com/yy/html/rank.html?from=homepage")
