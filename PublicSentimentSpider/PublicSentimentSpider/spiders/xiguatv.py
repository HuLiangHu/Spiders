# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urlencode
import re
import json
import time
import random


import execjs


def getSign():
    with open("./xigua.js", encoding='utf-8') as f:
        jsData = f.read()
    js = execjs.compile(jsData)
    sign = js.call('i')
    return sign
class XiguatvSpider(scrapy.Spider):
    name = 'xiguatv'
    #allowed_domains = ['xigua.com']
    baseurl = 'https://www.ixigua.com/api/pc/feed/?'

    headers = {
        'cookie': 'UM_distinctid=167968063b6e21-002fa99a22143c-35617600-13c680-167968063b73be; CNZZDATA1262382642=287634404-1544417995-https%253A%252F%252Fwww.google.com%252F%7C1544417995; WEATHER_CITY=%E5%8C%97%E4%BA%AC; _ga=GA1.2.354456000.1544418256; _gid=GA1.2.1830961456.1544418256; tt_webid=6633225899095934478',
        'referer': 'https://www.ixigua.com/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
    }


    parmas = {
        'max_behot_time': str(int(time.time()) - int(random.randint(600, 1800))),
        'category': 'video_new',
        'utm_source': 'toutiao',
        'widen': '1',
        'tadrequire': 'true',
        'as': getSign()['as'],
        'cp': getSign()['cp'],
        '_signature': 'QrLBfhASHsH9xDCYivOmoEKywW'
    }

    def start_requests(self):
        url = self.baseurl + urlencode(self.parmas)
        yield scrapy.Request(url,headers=self.headers)
    def parse(self, response):
        for i in json.loads(response.text)['data']:
            item = {}
            try:
                item['title'] = i['title']
                item['article_genre'] = i['article_genre']
                item['comments_count'] = i['comments_count']
                item['chinese_tag'] = i['chinese_tag']
                behot_time = i['behot_time']
                item['behot_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(behot_time))
                item['source'] = i['source']
                item['video_duration_str'] = i['video_duration_str']
                item['video_play_count'] = i['video_play_count']
                yield item
            except:
                pass
        try:
            max_behot_time = json.loads(response.text)['next']['max_behot_time']
            self.parmas['max_behot_time'] = max_behot_time
            new_url = self.baseurl + urlencode(self.parmas)
            # time.sleep(3)
            yield scrapy.Request(new_url,headers=self.headers)
        except:
            url = self.baseurl+urlencode(self.parmas)
            yield scrapy.Request(url,headers=self.headers)

