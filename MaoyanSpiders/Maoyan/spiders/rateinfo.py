# -*- coding: utf-8 -*-
import scrapy
import json
import re

class RateinfoSpider(scrapy.Spider):
    name = 'rateinfo'
    # allowed_domains = ['maoyan.com']
    start_urls = ['http://piaofang.maoyan.com/rankings/year?year=2018']

    headers ={
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    }
    def start_requests(self):
        yield scrapy.Request(self.start_urls[0],headers=self.headers,dont_filter=True)
    def parse(self, response):

        for info in response.xpath('//div[@id="ranks-list"]/ul[@class="row"]'):
            item={}
            item['name'] = info.xpath('.//p[@class="first-line"]/text()').extract_first()
            item['opentime'] = info.xpath('.//p[@class="second-line"]/text()').re_first('(.*)上映')
            link = info.xpath('./@data-com').extract_first()
            url = 'http://piaofang.maoyan.com/movie/'+re.search('(\d+)',link).group(1)
            print(url)
            yield scrapy.Request(url,meta={'item':item},callback=self.parse_item,headers=self.headers)

    def parse_item(self, response):
        item =response.meta['item']
        item['rating_num'] =response.xpath('//span[@class="rating-num"]/text()').extract_first()
        score_count= response.xpath('//p[@class="detail-score-count"]/text()').extract_first()
        try:
            item['score_count'] = self.parseString(re.search('(.*)观众评分',score_count).group(1))
        except:
            item['score_count'] =None
        want_count =response.xpath('//p[@class="detail-wish-count"]/text()').extract_first()
        try:
            item['want_count'] =self.parseString(re.search('(.*)人想看 ',want_count).group(1))
        except:
            item['want_count'] =None
        try:
            item['IMDb'] =re.search('IMDb (.*)',response.xpath('//p[@class="detail-other-score"]/text()').extract_first()).group(1)
        except:
            item['IMDb'] =None
        yield item
    def parseString(self, strValue):

        data = float(re.search('(\d+)', strValue).group(1))
        if '万' in strValue:
            result = data * 10000
        elif '亿' in strValue:
            result = data * 100000000
        else:
            result = data
        return result