# -*- coding: utf-8 -*-
from datetime import datetime
from urllib.parse import urlencode, quote
import json
import scrapy
import re

class DoubanbookinfoSpider(scrapy.Spider):
    name = 'doubanbookinfo'
#     allowed_domains = ['douban.com']
#     start_urls = 'https://book.douban.com/tag/{0}?start={1}&type=T'
#     booktypelist =['小说','外国文学','文学','中国文学','经典','日本文学','名著','当代文学',
#                    '外国名著','传记','回忆录','成长','励志','女性','职场']
#
#     def start_requests(self):
#         for booktype in self.booktypelist:
#             for page in range(50):
#                 url = self.start_urls.format(quote(booktype),str(int(page)*20))
#                 yield scrapy.Request(url,meta={'type':booktype})
#
 #########测试
    # def start_requests(self):
    #
    #     url ='https://www.douban.com/search?cat=1001&q=%E8%BF%BD%E9%A3%8E%E7%AD%9D%E7%9A%84%E4%BA%BA'
    #     yield scrapy.Request(url)
#########

    def start_requests(self):
        import pandas as pd
        for bookname in  pd.read_excel('.\spiders\出版物豆瓣作品列表.xlsx')['作品关键词']:
            url = 'https://www.douban.com/search?cat=1001&q={}/'.format(quote(str(bookname),encoding='utf-8'))
            yield scrapy.Request(url,meta={'bookname':bookname})

    def parse(self, response):

        for info in response.xpath('//div[@class="content"]'):
            item ={}

            item['bookname'] = info.xpath('div[@class="title"]/h3/a/text()').extract_first().strip()
            item['bookid'] = info.xpath('div[@class="title"]/h3/a/@onclick').re_first('sid: (\d+)')
            item['url'] ='https://book.douban.com/subject/{}/'.format(item['bookid'])
            item['grade'] = info.xpath('.//div[@class="rating-info"]/span[2]/text()').extract_first()
            try:
                if '人' in item['grade']:
                    item['gradepeople'] = 0
                else:
                    gradepeople=info.xpath('.//div[@class="rating-info"]/span[3]/text()').extract_first().strip()
                    item['gradepeople'] =re.search('(\d+)',gradepeople).group(1)
            except:
                item['gradepeople']=0
            try:
                star = info.xpath('.//div[@class="rating-info"]/span[1]/@class').re_first('(\d+)')
                item['star'] = int(star)/10
            except:
                item['star'] = None
            try:
                publish_time = response.xpath('.//span[@class="subject-cast"]/text()').extract_first()
                item['publish_time'] = publish_time.split('/')[-1]
            except:
                publish_time = response.xpath('.//div[@class="rating-info"]/span/text()').extract_first()
                item['publish_time'] = publish_time.split('/')[-1]
            try:
                item['publish_company'] = publish_time.split('/')[-2]
            except:
                item['publish_company'] = None
            try:
                item['author'] = publish_time.split('/')[0]
            except:
                item['author'] = None
            item['keyword'] = response.meta['bookname']
            item['crawldate'] = str(datetime.now()).split('.')[0]
            yield item
    #         yield scrapy.Request(item['url'],callback=self.parse_more,meta={'item':item})
    #
    #
    #
    # def parse_more(self, response):
    #     item = response.meta['item']
    #     try:
    #         item['author'] = response.xpath('//span[contains(text(),"作者")]/following-sibling::a/text()').extract_first().strip('\n').strip()
    #     except:
    #         item['author'] =None
    #
    #     translator = response.xpath('//span[contains(text(),"译者")]/following-sibling::a/text()').extract()
    #
    #     try:
    #         item['translator'] = '/'.join(translator)
    #
    #     except:
    #         item['translator'] =None
    #     try:
    #         item['ISBN'] = re.search('ISBN:</span> (.*?)<br/>',response.text).group(1)
    #     except:
    #         item['ISBN'] =None
    #     item['crawldate'] = str(datetime.now()).split('.')[0]
    #     yield item
    # #         yield scrapy.Request(item['url'],callback=self.parse_intro,meta={'item':item})
    # #
    # #
    # # def parse_intro(self, response):
    # #     item = response.meta['item']
    # #
    # #     introduction =response.xpath('string(//span[@class="all hidden"]/div/div[@class="intro"])').extract_first()
    # #     if introduction:
    # #         item['introduction'] = introduction
    # #     else:
    # #         item['introduction'] = response.xpath('string(//div[@class="intro"])').extract_first()
    # #
    # #     yield item