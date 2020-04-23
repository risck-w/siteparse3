import requests
from Utils.Utils import Util
import json
import re
import time
from spider.baseSiteParser import BaseSiteParser, ScpParser


class QQMusic(BaseSiteParser):

    def __init__(self, webDriver=False):
        self.driver = Util(webDriver=webDriver)
        self.domain = 'qq.com'
        self.ScpParser = ScpParser()

    def parser(self, url=None):
        self.parse_item()

    def parse_item(self, url=None):

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
        }
        self.ScpParser.set_headers(headers)

        # 榜单列表
        url = "https://c.y.qq.com/v8/fcg-bin/fcg_v8_toplist_opt.fcg?page=index&format=html&tpl=macv4&v8debug=1&jsonCallback=jsonCallback"
        music_list_content = self.driver.web_fetch2(url=url)
        music_list_content = music_list_content.replace("jsonCallback([", '')
        music_list = music_list_content.replace(']\n)', '')
        music_list = re.sub('\s', '', music_list)
        mlist = music_list.split('},{"GroupID')
        music = []
        music.append(mlist[0]+"}")
        music.append('{"GroupID'+mlist[1])
        songs_url = []
        for info in music:
            dict_info = json.loads(info)
            for songs in dict_info['List']:
                type = None
                if songs["type"] == 0:
                    type = "top"
                elif songs["type"] == 1:
                    type = "global"
                songs_url.append("https://c.y.qq.com/v8/fcg-bin/fcg_v8_toplist_cp.fcg?tpl=3&page=detail&date="+
                                 str(songs["update_key"])+"&topid="+str(songs["topID"])+
                                "&type="+type+"&song_begin=0&song_num=1000&g_tk=2090557760&loginUin=0&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0")
        for info in songs_url:
            content = self.driver.web_fetch2(url=info)
            songlist = json.loads(content)["songlist"]
            songInfo = {}
            for song in songlist:  # 获取歌曲信息： title, id
                songInfo[song["data"]['songmid']] = song["data"]['songname']
            self.get_songs_url(songs_dict=songInfo)

    def get_songs_url(self, songs_dict):
        for songmid in songs_dict:
            songUrl = "https://u.y.qq.com/cgi-bin/musicu.fcg?-=getplaysongvkey6968340363373204&g_tk=2090557760&loginUin" \
                      "=0&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0" \
                      "&data=%7B%22req%22%3A%7B%22module%22%3A%22CDN.SrfCdnDispatchServer%22%2C%22method%22%3A%22" \
                      "GetCdnDispatch%22%2C%22param%22%3A%7B%22guid%22%3A%224164181875%22%2C%22calltype%22%3A0%2C%22" \
                      "userip%22%3A%22%22%7D%7D%2C%22req_0%22%3A%7B%22module%22%3A%22vkey.GetVkeyServer%22%2C%22method" \
                      "%22%3A%22CgiGetVkey%22%2C%22param%22%3A%7B%22guid%22%3A%224164181875%22%2C%22songmid%22%3A%5B" \
                      "%22"+songmid+"%22%5D%2C%22songtype%22%3A%5B0%5D%2C%22uin%22%3A%22NaN%22%2C%22loginflag%22%3A" \
                      "1%2C%22platform%22%3A%2220%22%7D%7D%2C%22comm%22%3A%7B%22uin%22%3Anull%2C%22format%22%3A%22json%22" \
                      "%2C%22ct%22%3A24%2C%22cv%22%3A0%7D%7D"
            content = self.driver.web_fetch2(songUrl)
            try:
                req = json.loads(content)["req_0"]
                purl = req["data"]["midurlinfo"][0]["purl"]
                sip = req["data"]["sip"][0]
                if purl is None or sip is None:
                    continue
                music_url = sip+purl
                self.ScpParser.set_vod_music(music_url)

            except Exception as e:
                print(e)

            break

    def get_result(self):
        return self.ScpParser.get_params()