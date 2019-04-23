# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals


class RandomProxy(object):

    def __init__(self, iplist):
        self.iplist = iplist
        self.proxy = self.get_Random_Proxy()

    @classmethod
    def from_crawler(cls, crawler):
        # 在settings中加载IPLIST的值
        return cls(
            iplist=crawler.settings.getlist('IPLIST')
        )
#http://1.64.217.90:8118
    # def process_request(self, request, spider):
    #
    #     request.meta['proxy']= self.proxy
    #     #request.meta['download_timeout'] = 10
    #     print('代理ip:' + request.meta['proxy'])


    def get_Random_Proxy(self):
        import requests
        PROXY_POOL_URL = 'http://localhost:5555/random'
        response = requests.get(PROXY_POOL_URL)
        proxy = 'http://' + str(response.text)
        return proxy


    def process_response(self, request, response, spider):
        # 如果该ip不能使用，更换下一个ip
        # 在请求上添加代理

        if response.status != 200 :
                request.meta['proxy'] = self.get_Random_Proxy()
                print('更换ip:' + request.meta['proxy'])
                return request
                with open('miss.txt','a') as f:
                    f.write(response.url)
                    f.write('\n')
        return response

    def process_exception(self,request,exception,spider):
        if exception:
            proxy = self.get_Random_Proxy()
            request.meta['proxy'] =proxy
            print('超时代理ip:',request.meta['proxy'])

