# -*- coding: utf-8 -*-

import random
from scrapy import signals
from scrapy.http import HtmlResponse
import logging
from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
    ConnectionRefusedError, ConnectionDone, ConnectError, \
    ConnectionLost, TCPTimedOutError
from twisted.web.client import ResponseFailed
from scrapy.core.downloader.handlers.http11 import TunnelError
logger =logging.getLogger(__name__)

import requests


def get_proxy():
    return requests.get("http://127.0.0.1:8080/get/").text

# class get_Random_Proxy:
#
#     def get_proxy(self):
#         return requests.get("http://127.0.0.1:8080/get/").text
#
#     def delete_proxy(self, proxy):
#         requests.get("http://127.0.0.1:8080/delete/?proxy={}".format(proxy))
#
#     #your spider code
#
#     def getHtml(self):
#         # ....
#         retry_count = 5
#         proxy = self.get_proxy()
#         while retry_count > 0:
#             try:
#                 html = requests.get('https://www.qidian.com', proxies={"http": "http://{}".format(proxy)})
#                 # 使用代理访问
#                 if html.status_code == 200:
#                     return 'http://'+proxy
#                 else:
#                     proxy = self.get_proxy()
#                     return 'http://'+proxy
#             except Exception:
#                 retry_count -= 1
#         # 出错5次, 删除代理池中代理
#         self.delete_proxy(proxy)
#         return None
# randomip = get_Random_Proxy()

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
        #self.proxy = self.get_Random_Proxy()

    @classmethod
    def from_crawler(cls, crawler):
        # 在settings中加载IPLIST的值
        return cls(
            iplist=crawler.settings.getlist('IPLIST')
        )
#http://1.64.217.90:8118
    def process_request(self, request, spider):
        # if 'www.hongxiu' in request.url:
            request.meta['proxy'] = 'http://'+get_proxy()
            #request.meta['proxy']= self.get_Random_Proxy()
            request.meta['download_timeout'] = 30
            logger.debug('代理ip:' + request.meta['proxy'])





    def process_response(self, request, response, spider):
        # 如果该ip不能使用，更换下一个ip
        # 在请求上添加代理

        if response.status != 200 :
                request.meta['proxy'] = 'http://'+get_proxy()
                print('更换ip:' + request.meta['proxy'])
                return request
        return response

    def process_exception(self,request,exception,spider):
        if exception:
            logger.debug('Got exception: %s' % (exception))

            request.meta['proxy'] ='http://'+get_proxy()
            print('超时代理ip:',request.meta['proxy'])


class ProcessAllExceptionMiddleware(object):
    ALL_EXCEPTIONS = (defer.TimeoutError, TimeoutError, DNSLookupError,
                      ConnectionRefusedError, ConnectionDone, ConnectError,
                      ConnectionLost, TCPTimedOutError, ResponseFailed,
                      IOError, TunnelError)
    def process_response(self,request,response,spider):
        #捕获状态码为40x/50x的response
        if str(response.status).startswith('4') or str(response.status).startswith('5'):
            #随意封装，直接返回response，spider代码中根据url==''来处理response

            return request
        #其他状态码不处理
        return response
    def process_exception(self,request,exception,spider):
        #捕获几乎所有的异常
        if exception:
            #在日志中打印异常类型
            logger.debug('Got exception: %s' % (exception))
            #随意封装一个response，返回给spider
            logger.debug(request.url)
            request.meta['proxy'] = 'http://'+get_proxy()
            request.meta['download_timeout'] = 30
            logger.debug('更换ip:' + request.meta['proxy'])
            return request
        #打印出未捕获到的异常
        logger.debug('not contained exception: %s'%exception)

    def get_Random_Proxy(self):
        import requests
        PROXY_POOL_URL = 'http://localhost:5555/get'
        response = requests.get(PROXY_POOL_URL)
        proxy = 'http://' + str(response.text)
        return proxy