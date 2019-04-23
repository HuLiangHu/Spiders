# -*- coding: utf-8 -*-

import random
import logging
logger =logging.getLogger(__name__)


class RandomUserAgent(object):
    def __init__(self, user_agent):
        self.user_agent = user_agent

    @classmethod
    def from_crawler(cls, crawler):
        # 从settings中加载USER_AGENT的值
        return cls(
            user_agent=crawler.settings.getlist('USER_AGENT')
        )

    def process_request(self, request, spider):
        # 在process_request中设置User-Agent的值
        request.headers.setdefault('User-Agent', random.choice(self.user_agent))

class RandomProxy(object):

    def __init__(self, iplist=None):
        self.iplist = iplist
        self.proxyServer = "http://transfer.mogumiao.com:9001"
        self.proxyAuth = "Basic " + "bUVQZzdBYWZiUXl6QU9veDo0T1NoRUZyNXVWa0JFN0Q2" # appkey为你订单的key

    def process_request(self, request, spider):
        request.meta["proxy"] = self.proxyServer
        request.headers["Authorization"] = self.proxyAuth
        request.meta['download_timeout'] = 30