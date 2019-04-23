# -*- coding: utf-8 -*-
from datetime import datetime

import scrapy
from urllib.parse import urlencode
import json
import time
from MovieComments.items import MoviecommentsItem


class PptvSpider(scrapy.Spider):
    name = 'pptv'
    # allowed_domains = ['pptv.com']
    # start_urls = ['http://apicdn.sc.pptv.com/sc/v4/pplive/ref/vod_9041400/feed/list?']
    baseurl ='http://apicdn.sc.pptv.com/sc/v4/pplive/ref/vod_9041400/feed/list?'
    headers = {
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        'Referer':'http://v.pptv.com/page/ibEslowtx4RibCAMw.html?rcc_id=baiduchuisou',
        'Host':'apicdn.sc.pptv.com'
    }
    def start_requests(self):
        for page in range(10):
            parmas = {
                'appplt': 'web',
                'action': '1',
                'pn': page,
                'ps': '20',
            }
            url= self.baseurl+urlencode(parmas)
            yield scrapy.Request(url,headers=self.headers)
    def parse(self, response):
        info = json.loads(response.text)
        for i in info['data']['page_list']:
            item =MoviecommentsItem()
            item['comment'] = i['content']
            item['author'] = i['user']['nick_name']
            comment_time = i['create_time']
            item['comment_time'] =time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(comment_time/1000))
            item['ctime'] = str(datetime.now())
            yield item

