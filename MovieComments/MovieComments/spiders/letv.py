# -*- coding: utf-8 -*-
from urllib.parse import urlencode

import scrapy
import re
from datetime import datetime
import time
import json

class LetvSpider(scrapy.Spider):
    name = 'letv'
    #allowed_domains = ['letv.com']
    #详情页
    start_urls = ['http://www.le.com/tv/93893.html']
    commenturl ='http://api.my.le.com/vcm/api/list?'

    def parse(self, response):
        for info in response.xpath('//div[starts-with(@class,"show_cnt twxj")]'):
            video_urls = info.xpath('.//dd/a/@href').extract()
            for video_url in video_urls:
                yield scrapy.Request(video_url,callback=self.parse_comment)

    def parse_comment(self, response):
        item = {}
        pid = re.search('(\d+)',self.start_urls[0]).group(1)
        xid = re.search('(\d+)',response.url).group(1)
        total_comment_count = re.search('vid_comm_count: \'(\d+)',response.text).group(1)
        item['title'] = re.search('title:\"(.*)\"',response.text).group(1)
        for page in range(1,int(int(total_comment_count)/20)+1):
            parmas ={
                'type': 'video',
                'page': page,
                'sort':'',
                'cid': '2',
                'xid': xid,
                'pid': pid,
                '_': int(time.time()*1000)
            }
            url = self.commenturl+urlencode(parmas)
            yield scrapy.Request(url,callback=self.parse_item,meta={'item':item})

    def parse_item(self, response):
        item =response.meta['item']
        for info in json.loads(response.text)['data']:
            item['comment'] = info['content']
            item['author'] = info['user']['username']
            comment_time = info['ctime']
            item['comment_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(comment_time)))
            item['ctime'] = str(datetime.now())

            yield item
