# -*- coding: utf-8 -*-
# __author__ = hul
from datetime import datetime

import scrapy
import json
import re
import time
import requests
from scrapy import Selector
from urllib.parse import urlencode
from .getData import getkeyWord

class BaiduinfoSpider(scrapy.Spider):
    name = 'baiduinfo'
    # allowed_domains = ['baidu.com']
    start_urls = 'https://www.baidu.com/s?'
    keywords = getkeyWord()

    def start_requests(self):
        for keyword in self.keywords:
            for page in range(2):
                parmas ={
                    'ie':'utf - 8',
                    'cl':'2',
                    'rtt':'1',
                    'tn':'news',
                    'word':keyword,
                    'pn':str(int(page)*10)

                }
                url =self.start_urls+urlencode(parmas)
                yield scrapy.Request(url)

    def parse(self, response):
        for info in  response.xpath('//div[@class="result"]'):
            item ={}
            item['title'] = info.xpath('string(h3/a)').extract_first().strip()
            item['url'] = info.xpath('h3/a/@href').extract_first()
            source_time =info.xpath('div//p[@class="c-author"]/text()').extract_first().split('\xa0\xa0\t\t\t\t\n\t\t\t\t\t\t')
            item['source'] = source_time[0]
            item['pubtime'] = source_time[1].strip()
            content = info.xpath('string(div)').extract_first().strip('')
            item['content']=re.search(r'\n\t\t\t\n    (.*)...',content).group(1)
            item['crawldate'] = str(datetime.now()).split('.')[0]

            yield item
