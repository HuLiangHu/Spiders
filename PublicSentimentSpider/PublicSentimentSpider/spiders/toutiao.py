# -*- coding: utf-8 -*-
# __author__ = hul
import scrapy
from urllib.parse import urlencode
import time
from datetime import datetime
import json

class ToutiaoSpider(scrapy.Spider):
    name = 'toutiao'
    start_urls = 'https://www.toutiao.com/search_content/?'
    keyword = '刘亦菲'

    def start_requests(self):
        for page in range(0,1):
            parmas = {
                'offset': str(int(page)*20),
                'format': 'json',
                'keyword': self.keyword,
                'autoload': 'true',
                'count': '20',
                'cur_tab': '1',
                'from':'search_tab'
            }
            url = self.start_urls+urlencode(parmas)
            yield scrapy.Request(url)
    def parse(self, response):
        for info in json.loads(response.text)['data']:
            item={}
            try:
                item['title'] = info['title']
                item['author'] =info['media_name']
                item['url'] =info['article_url']
                item['comment_count'] =info['comment_count']
                item['content'] =info['abstract']
                item['pubtime'] =info['datetime']
                item['crawldate'] = str(datetime.now()).split('.')[0]
                yield item
            except:
                pass
