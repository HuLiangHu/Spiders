# -*- coding: utf-8 -*-
# __author__ = hul
# __date__ = 2018/10/23 下午9:10

from urllib.parse import urlencode

import scrapy
import re
import json
import time
from datetime import datetime

class TencentdmSpider(scrapy.Spider):
    name = 'DMtencent'
    # 视频详情页
    start_urls = ['http://v.qq.com/detail/n/n7tkhkv2tgd4sjd.html?ptag=baidu.aladdin.tv.pay']
    danmu_richdata = 'https://bullet.video.qq.com/fcgi-bin/target/regist?'
    danmu_baseurl ='https://mfm.video.qq.com/danmu?'

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0],callback=self.parse_targetid)

    def parse_targetid(self, response):
        title = 0
        cid = re.search('http://v.qq.com/detail/.*?/(.*).html',response.url).group(1)
        items = response.xpath('//span[@class="item"]')
        for item in items:
            flag = item.xpath('a/span[@class="mark_v"]/img/@alt').extract_first()
            if flag !="预告":

                url = item.xpath('a/@href').extract_first()
                vid = re.search('vid=(.*)',url).group(1)
                parmas = {
                    'otype':'json',
                    'vid':vid,
                    'cid':cid,
                    'lid':'',
                    'g_tk':'',
                    '_':int(time.time()*1000),
                }
                url = self.danmu_richdata+urlencode(parmas)
                title = title+1
                yield scrapy.Request(url,meta={'title':title},callback=self.parse_danmu)
#################
    # """
    # 综艺"""
    # def parse(self, response):
    #     for i in response.xpath('//li[@class="list_item"]'):
    #         url = i.xpath('a/@href').extract_first()
    #         title = i.xpath('a/@title').extract_first()
    #         url = re.sub('http','https',url)
    #         yield scrapy.Request(url,callback=self.parse_targetid,meta={'title':title})
    #
    # def parse_targetid(self, response):
    #     '"http://v.qq.com/x/cover/wonlykhit7tk22n.html?vid=n00284ubl8m'
    #     vid = re.search('.*vid=(.*)',response.url).group(1)
    #     cid = re.search('.*\/cover/(.*).html',response.url).group(1)
    #
    #     parmas = {
    #                 'otype':'json',
    #                 'vid':vid,
    #                 'cid':cid,
    #                 'lid':'',
    #                 'g_tk':'',
    #                 '_':int(time.time()*1000),
    #                 }
    #     url = self.danmu_richdata+urlencode(parmas)
    #
    #     yield scrapy.Request(url,meta={'title':response.meta['title']},callback=self.parse_danmu)

#############################

    def parse_danmu(self, response):
        title = response.meta['title']
        targetid= re.search('targetid=(\d+)',response.text).group(1)
        for timestamp in range(15,4000,30):
            parmas ={
                'otype':'json',
                'timestamp':timestamp,
                'target_id':targetid,
                'count':'80',
                'second_count':'5',
                '_': int(time.time()*1000),
            }
            url = self.danmu_baseurl+urlencode(parmas)
            yield scrapy.Request(url,callback=self.parse_item,meta={'title':title})
    def parse_item(self,response):

        item={}
        for comment in json.loads(response.text)['comments']:
            item['author'] =comment['opername']
            item['comment'] =comment['content']
            item['comment_time'] =str(comment['timepoint'])+'S'
            item['ctime'] = str(datetime.now())
            item['title'] ='第'+str(response.meta['title'])+'集'
            yield item