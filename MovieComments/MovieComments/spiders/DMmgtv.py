# -*- coding: utf-8 -*-
from urllib.parse import urlencode

import scrapy
import re
import json
import time
import random

class DmmgtvSpider(scrapy.Spider):
    name = 'DMmgtv'
    start_urls = 'https://www.mgtv.com/h/328268.html?cxid=95kqkw8n6'
    danmuapi = 'https://galaxy.bz.mgtv.com/rdbarrage?'
    videoapi = 'https://pcweb.api.mgtv.com/episode/list?'  # 每个视频链接

    cid = re.search('(\d+)',start_urls).group(1)
    timestemp =time.time() * 1000
    def start_requests(self):
        # 电视剧
        # collection_id = re.search('(\d+)', self.start_urls).group(1)
        parmas = {
            'collection_id': self.cid,
            '_support': '10000000',
            '_': int(self.timestemp)
        }
        url = self.videoapi + urlencode(parmas)
        yield scrapy.Request(url, callback=self.parse_prevideo)

    def parse_prevideo(self, response):
        title = json.loads(response.text)['data']['info']['title']
        for info in json.loads(response.text)['data']['list']:
            vid = info['video_id']
            videourl ='https://www.mgtv.com'+info['url']
            episode =info['t1']

            parmas={
                'version':'1.0.0',
                'vid':vid,
                'abroad':'0',
                'pid':'',
                'os':'',
                'uuid':'',
                'deviceid':'',
                'cid':self.cid,
                'ticket':'',
                'time':str(int(self.timestemp))[-4:],
                'mac':'',
                'platform':'0',
            }
            interval =0
            url = self.danmuapi+urlencode(parmas)
            yield scrapy.Request(url,callback=self.parse_item,meta={'title':title,
                                                                    'episode':episode,
                                                                    'videourl':videourl,
                                                                    'parmas':parmas,
                                                                    'interval':interval})


    def parse_item(self, response):
        if json.loads(response.text)['data']['items']:
            for info in json.loads(response.text)['data']['items']:
                item = {}
                item['content'] = info['content']
                item['uid'] = info['uid']
                item['title'] =response.meta['title']
                item['episode'] = response.meta['episode']
                item['videourl'] = response.meta['videourl']
                item['pubtime'] = str(response.meta['interval'])+'--'+str(int(response.meta['interval'])+1)+'分'
                yield item
            parmas =response.meta['parmas']
            parmas['time'] = json.loads(response.text)['data']['next']

            interval = int(response.meta['interval'])+1
            url = self.danmuapi + urlencode(parmas)
            yield scrapy.Request(url, callback=self.parse_item, meta={'parmas': parmas,
                                                                      'interval':interval,
                                                                      'title':response.meta['title'],
                                                                      'episode': response.meta['episode'],
                                                                      'videourl': response.meta['videourl'],
                                                                      'interval':interval
                                                                      })

