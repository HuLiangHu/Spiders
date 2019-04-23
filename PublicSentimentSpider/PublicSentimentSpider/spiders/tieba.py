# -*- coding: utf-8 -*-
# __author__ = hul
import scrapy
from urllib.parse import urlencode
import json
import re
from datetime import datetime
import time
import requests
import pandas as pd
from scrapy import Selector
from .getData import getkeyWord

class TiebaSpider(scrapy.Spider):
    name = 'tieba'

    headers = {
        'referer': 'https://tieba.baidu.com/index.html',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }
    #start_urls = 'http://tieba.baidu.com/hottopic/browse/getTopicRelateThread?'

   # start_urls = 'http://tieba.baidu.com/hottopic/browse/getTopicRelateThread?'
    start_urls ='http://tieba.baidu.com/f/search/res?'
    keywords = getkeyWord()


    def start_requests(self):

        # for keyword in self.keywords:
            keyword ='你和我的倾城时光吧'
            for pn in range(1,80):
                parmas ={
                    'isnew': '1',
                    'kw':'' ,
                    'qw': keyword,
                    'rn': '10',
                    'un':'',
                    'only_thread': '1',
                    'sm': '1',
                    'sd':'',
                    'ed':'',
                    'pn': pn,
                }
                url = self.start_urls+urlencode(parmas,encoding='gb2312')
                yield scrapy.Request(url,meta={'keyword':keyword,'proxy':'http://203.95.222.206:31323'})
                self.headers['referer'] =url


    def parse(self, response):
        if "很抱歉没有找到与" not in response.text:
            for info in  response.xpath('//div[@class="s_post"]'):

                item = {}
                item['title'] = info.xpath('string(span[@class="p_title"]/a)').extract_first()
                item['source'] = info.xpath('a[1]/font[@class="p_violet"]/text()').extract_first()
                item['pubtime'] =info.xpath('font[@class="p_green p_date"]/text()').extract_first()
                item['author'] = info.xpath('a[2]/font[@class="p_violet"]/text()').extract_first()
                url =info.xpath('span[@class="p_title"]/a/@href').extract_first()
                if 'tieba.baidu.com' in url:
                    item['url'] = url
                else:
                    item['url'] ='http://tieba.baidu.com'+url
                item['keyword'] =response.meta['keyword']
                item['crawldate'] = str(datetime.now()).split('.')[0]

                yield scrapy.Request(item['url'],meta={'item':item},callback=self.parse_replynum)
        with open('miss.txt','a') as f:
            f.write(response.meta['keyword'])
            f.write('\n')
    def parse_replynum(self, response):
        item = response.meta['item']
        try:
            item['content'] = response.xpath('//div[starts-with(@id,"post_content")]/text()').extract_first().strip()
        except:
            item['content'] = response.xpath('//div[starts-with(@id,"post_content")]/text()').extract_first()
        item['replynum'] = response.xpath('//li[@class="l_reply_num"]/span/text()').extract_first()
        yield item









    # def start_requests(self):
    #
    #     url = self.start_urls+urlencode(self.parmas)
    #     yield scrapy.Request(url)
    # def parse(self, response):
    #
    #     totalpage = json.loads(response.text)['data']['page']['current_num']
    #     for page in range(1,totalpage):
    #
    #         self.parmas['page_no'] =page
    #         url = self.start_urls+urlencode(self.parmas)
    #         yield scrapy.Request(url,callback=self.parse_detail)
    #
    # def parse_detail(self, response):
    #     for info in json.loads(response.text)['data']['thread_list']:
    #         item={}
    #         item['title'] =info['title']
    #
    #         item['source'] =info['forum_name']+'吧'
    #         item['author'] =info['author']['name']
    #         sex =info['author']['sex']
    #         if sex =='2':
    #             item['sex'] ="F"
    #         elif sex == '1':
    #             item['sex']= 'M'
    #         else:
    #             item['sex'] ='不详'
    #         item['view_num'] = info['view_num']
    #         pubtime = info['last_time_int']
    #         item['pubtime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(pubtime))
    #         item['reply_num'] =info['reply_num']
    #         item['content'] = info['abstract']
    #         item['crawldate'] = str(datetime.now()).split('.')[0]
    #
    #         yield item
    #
    #
