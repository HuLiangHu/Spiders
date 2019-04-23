# -*- coding: utf-8 -*-
from datetime import datetime
import re
import scrapy
import time
import json
from urllib.parse import urlencode

from MovieComments.items import MoviecommentsItem


class SohuSpider(scrapy.Spider):
    name = 'sohu'
    allowed_domains = ['tv.sohu.com']
    start_urls = ['http://tv.sohu.com/']

    def start_requests(self):
        yield scrapy.Request('https://tv.sohu.com/s2017/tssban/')

    def parse(self, response):
        # maxpage = response.xpath('//div[@id="pagination_1"]/a[9]/text()').extract_first()
        # print(maxpage)
        topic_id = re.search('playlistId = "(\d+)"',response.text).group(1)
        baseurl = 'https://api.my.tv.sohu.com/comment/api/v1/load?'
        timestamp = int(time.time() * 1000)
        for page in range(1,308):
            parmas = {
                'topic_id': topic_id,
                'topic_type': '2',
                'source': '2',
                'page_size': '10',
                'sort': '0',
                'timestamp': str(timestamp),
                'ssl': '0',
                'page_no': page,
                'reply_size': '2',
                '_': str(timestamp + 2),
            }
            url = baseurl+urlencode(parmas)
            print(url)
            yield scrapy.Request(url,callback=self.parse_detail)

    def parse_detail(self,response):
        content = json.loads(response.text)
        for i in content['data']['comments']:
            item = {}
            item['comment'] = i['content']
            comment_time =i['createtime']
            item['comment_time']= time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(comment_time/ 1000))
            item['ctime'] = str(datetime.now())
            item['like_count'] =i['like_count']
            yield item