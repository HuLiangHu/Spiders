# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import random
from scrapy import signals
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

    def __init__(self, iplist):
        self.iplist = iplist

    @classmethod
    def from_crawler(cls, crawler):
        # 在settings中加载IPLIST的值
        return cls(
            iplist=crawler.settings.getlist('IPLIST')
        )

    def process_request(self, request, spider):
        # 在请求上添加代理
        proxy = random.choice(self.iplist)

        request.meta['proxy'] = proxy
        request.meta['download_timeout'] = 30
        logger.debug('代理ip:' + request.meta['proxy'])
    def process_response(self, request, response, spider):
            # 如果该ip不能使用，更换下一个ip
            # 在请求上添加代理

        if response.status != 200 :
                request.meta['proxy'] = random.choice(self.iplist)
                logger.debug('更换ip:' + request.meta['proxy'])
                return request
        return response