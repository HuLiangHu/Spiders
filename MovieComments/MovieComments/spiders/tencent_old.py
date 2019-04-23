# -*- coding: utf-8 -*-
import re
from datetime import datetime

import json
import scrapy
import time
import requests
from MovieComments.items import MoviecommentsItem
from scrapy import Selector
from urllib.parse import urlencode


class OLDTencentSpider(scrapy.Spider):
    name = 'tencent_old'
    #allowed_domains = ['v.qq.com']
    start_urls = 'https://v.qq.com/detail/d/dzn1zjs53yvpvij.html'
    timestemp = int(time.time() * 1000)

    def start_requests(self):
        yield scrapy.Request(self.start_urls, callback=self.parse_pre_url)

    def parse_pre_url(self,response):
        episode = 0
        cid = re.search('http(.*)://v.qq.com/detail/.*?/(.*).html', response.url).group(1)
        items = response.xpath('//span[@class="item"]')
        for item in items:
            flag = item.xpath('a/span[@class="mark_v"]/img/@alt').extract_first()
            if flag != "预告":
                url = item.xpath('a/@href').extract_first()
                vid = re.search('vid=(.*)',url).group(1)
                baseurl = 'https://ncgi.video.qq.com/fcgi-bin/video_comment_id?'
                parmas = {
                    'otype': 'json',
                    'op': '3',
                    'vid': vid,
                    '_': int(time.time())
                }

                url = baseurl + urlencode(parmas)
                episode =episode+1
                yield scrapy.Request(url,meta={'episode':episode},callback=self.parse_next_video)


    def parse_next_video(self,response):

        episode = response.meta['episode']

        commentid = re.search('"comment_id":"(\d+)"',response.text).group(1)
        parmas ={
            'orinum': '10',
            'oriorder': 'o',
            'pageflag': '1',
            'cursor': '0',
            'scorecursor': '0',
            'orirepnum': '2',
            'reporder': 'o',
            'reppageflag': '1',
            'source': '9',
            '_': self.timestemp
        }
        url ='https://video.coral.qq.com/varticle/{}/comment/v2?'.format(commentid)+urlencode(parmas)
        yield scrapy.Request(url,meta={'parmas':parmas,'url':url,'episode':episode},callback=self.parse_next_commentpage,dont_filter=True)


    def parse_next_commentpage(self, response):
        targetid = json.loads(response.text)['data']['targetid']
        parmas = response.meta['parmas']
        parmas['cursor'] = int(json.loads(response.text)['data']['last'])
        parmas['_'] = self.timestemp
        for info in json.loads(response.text)['data']['oriCommList']:
            item = MoviecommentsItem()
            item['comment'] = info['content']
            item['author'] = None
            comment_time =info['time']
            item['comment_time'] =time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(comment_time)))
            item['ctime'] = str(datetime.now())
            item['title'] = '第'+str(response.meta['episode'])+'集'
            yield item
            url = 'https://video.coral.qq.com/varticle/{}/comment/v2?'.format(targetid) + urlencode(parmas)
            yield scrapy.Request(url, meta={'parmas': parmas,'episode':response.meta['episode']},callback=self.parse_next_commentpage)



