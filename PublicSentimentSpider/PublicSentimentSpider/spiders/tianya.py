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

class TianyaSpider(scrapy.Spider):
    name = 'tianya'
    start_urls = 'http://search.tianya.cn/bbs?'
    keyword = '你和我的倾城时光'

    def getMaxPage(self):
        url ='http://search.tianya.cn/bbs?q={}'.format(self.keyword)
        selector = Selector(requests.get(url))
        maxpage = selector.xpath('//div[@class="long-pages"]/a[last()-1]/text()').extract_first()
        return maxpage
    def start_requests(self):
        maxpage = self.getMaxPage()
        #for keyword in self.keywords:
        keyword ='你和我的倾城时光'
        for page in range(1,int(maxpage+1)):
            parmas ={
                'q':keyword,
                'pn':page
            }
            url = self.start_urls+urlencode(parmas)
            yield scrapy.Request(url)

    def parse(self, response):
        infos = response.xpath('//div[@class="searchListOne"]/ul/li')
        try:
            for info in infos:
                item={}
                item['title'] = info.xpath('string(div/h3/a)').extract_first()
                item['author'] =info.xpath('p[@class="source"]/a[2]/text()').extract_first()
                item['url'] =info.xpath('div/h3/a/@href').extract_first()
                item['putime']=info.xpath('p[@class="source"]/span[1]/text()').extract_first()
                item['source'] =info.xpath('p[@class="source"]/a[1]/text()').extract_first()
                item['reply_num'] =info.xpath('p[@class="source"]/span[2]/text()').extract_first()
                yield scrapy.Request(item['url'],meta={'item':item},callback=self.parse_detail)
        except:
            pass
    def parse_detail(self, response):
        item = response.meta['item']
        content = ' '.join(response.xpath('//div[starts-with(@class,"bbs-content")]/text()').extract())
        item['content'] = re.sub('\t','',content).replace('\u3000','').replace('\r\n','')
        view_num = response.xpath('//div[@class="atl-info"]/span[3]/text()').extract_first()
        item['view_num'] = re.search('点击：(.*)',view_num).group(1)
        item['crawldate'] = str(datetime.now()).split('.')[0]


        yield item