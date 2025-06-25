#!/usr/bin/python
# coding=utf8

from handler.crawler import crawler_handler
from handler.crawler import HotWebSite_Handler
from handler.crawler import WordCloud_Handler
from handler.crawler import Top_HotWebSite_Handler
from handler.crawler import Hello_handler,Noblock_handler
from handler.crawler import AI_Agent_search_handler
from handler.user import user_login_handler, users_handler, user_logout_handler


def get_routers():
    return [
        (r'/craw', crawler_handler),
        (r'/user/login', user_login_handler),
        (r'/user/add', users_handler),
        (r'/logout', user_logout_handler),
        (r'/topHotWebSite', Top_HotWebSite_Handler),
        (r'/hotWebSite', HotWebSite_Handler),
        (r'/wordCloud', WordCloud_Handler),
        (r'/hello', Hello_handler),
        (r'/noblock', Noblock_handler),
        (r'/AIAgentSearch', AI_Agent_search_handler)

    ]