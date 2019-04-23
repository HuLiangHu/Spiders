# -*- coding: utf-8 -*-
from datetime import datetime

import scrapy
import re
import json
class transCookie:
    def __init__(self, cookie):
        self.cookie = cookie
    def stringToDict(self):
        '''
        将从浏览器上Copy来的cookie字符串转化为Scrapy能使用的Dict
        :return:
        '''
        itemDict = {}
        items = self.cookie.split(';')
        for item in items:
            key = item.split('=')[0].replace(' ', '')
            value = item.split('=')[1]
            itemDict[key] = value
        return itemDict
def cookiemain():
    Cookie = 'SINAGLOBAL=8376945242285.543.1545639416752; TC-Page-G0=784f6a787212ec9cddcc6f4608a78097; _s_tentry=-; Apache=8113196790792.414.1545731017010; ULV=1545731017210:2:2:2:8113196790792.414.1545731017010:1545639416812; TC-V5-G0=866fef700b11606a930f0b3297300d95; login_sid_t=0eeeceee93967a18aa2fba9d441254f5; cross_origin_proto=SSL; Ugrow-G0=370f21725a3b0b57d0baaf8dd6f16a18; UOR=,,yunqi.qq.com; SCF=Al32yNLNqoM28nprrh8w35JDuptle04PYnU8A34kNlzrLhxBnBzQrdBJa3NrrLvKJXpLrYS00tFsCMcBjKIT8mo.; SUHB=09PNJ4P5-h6Ypd; SUB=_2AkMraKAEf8NxqwJRmP4RxWvkaYlywwnEieKdNFHfJRMxHRl-yj9jqmk8tRB6AOiO62kOwT0PlkSMTe5LP2MlFTIA5x1P; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9W5dY3bWc_cOkodmPr7_-fVf'

    trans = transCookie(Cookie)
    return trans.stringToDict()
cookies=cookiemain()
print(cookies)
class WeibofansSpider(scrapy.Spider):
    name = 'weibofans'
    #allowed_domains = ['weibo.com']
    start_urls = ['https://weibo.com/u/1428392852',
                  'https://weibo.com/xiayu',
                  'https://weibo.com/qiaozhenyu',
                  'https://weibo.com/u/5313535139']
    headers ={
        'Host': 'weibo.com',
        #'Referer': 'https://passport.weibo.com/visitor/visitor?entry=miniblog&a=enter&url=https%3A%2F%2Fweibo.com%2Fu%2F1428392852%3Fis_all%3D1&domain=.weibo.com&ua=php-sso_sdk_client-0.6.28&_rand=1546923826.5941',
        #'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url,headers=self.headers,cookies=cookies)
    def parse(self, response):
        #print(response.text)
        item={}
        item['name'] =re.search('CONFIG\[\'onick\'\]=\'(.*)\'',response.text).group(1)
        item['weibofans'] =re.search('的粉丝\((\d+)\)',response.text).group(1)
        item['ctime'] = str(datetime.now()).split('.')[0]
        yield item
