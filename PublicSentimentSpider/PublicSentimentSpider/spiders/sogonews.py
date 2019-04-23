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


class SogonewsSpider(scrapy.Spider):
    name = 'sogonews'
    keywords = getkeyWord()
    start_urls ='https://news.sogou.com/news?'

    def start_requests(self):
        for keyword in self.keywords:
            for page in range(1,2):
                parmas ={
                    'query':self.keyword,
                    'sort':'0',
                    'page':page,
                    '_asf':'news.sogou.com',
                    '_ast':str(int(time.time())),
                }
                url = self.start_urls+urlencode(parmas)
                yield scrapy.Request(url)

    def parse(self, response):

        for info in response.xpath('//div[starts-with(@class,"news1")]'):
            item={}
            item['title'] = info.xpath('h3/a/text()').extract_first()
            item['url'] = info.xpath('h3/a/@href').extract_first()

            source_time = info.xpath('div[@class="news-detail"]/div/p[@class="news-from"]/text()').extract_first()
            if source_time:
                item['source'] = re.search('(.*?) (.*?)',source_time).group(1)
                item['pubtime'] = re.search(r'{}.*?(.*)'.format(item['source']),source_time).group(1).strip()
                item['content'] = info.xpath('string(div[@class="news-detail"]/div/p[@class="news-txt"]/span)').extract_first().strip()
                item['crawldate'] = str(datetime.now()).split('.')[0]
                yield item