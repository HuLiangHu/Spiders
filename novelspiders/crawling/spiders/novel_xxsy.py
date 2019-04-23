# -*- coding: utf-8 -*-
import time
import re
import json

import pymysql
from crawling.items import SpiderNovelItem
# from redis_spider import scrapy.Spider
import scrapy
from scrapy.utils.project import get_project_settings


class XxsySpider(scrapy.Spider):
    name = "xxsy"
    # download_delay = 1
    # PAGE_SIZE = 400
    start_urls = ['http://www.xxsy.net/search?s_wd=&sort=1&pn=1']

    ################################
    # def start_requests(self):
    #     settings = get_project_settings()
    #     conn = pymysql.connect(
    #         user=settings['MYSQL_USER'],
    #         passwd=settings['MYSQL_PASSWD'],
    #         db=settings['MYSQL_DBNAME'],
    #         host=settings['MYSQL_HOST'],
    #         charset="utf8",
    #         use_unicode=True
    #     )
    #     cursor = conn.cursor()
    #     cursor.execute(
    #         'SELECT url FROM rawdata WHERE crawldate = "2018-11-28" AND site ="xxsy" AND page_view>20000 and word_count>15000 AND name not in (SELECT name FROM rawdata WHERE crawldate = "2018-12-30")'
    #     )
    #
    #     rows = cursor.fetchall()
    #     for row in rows:
    #         bookurl = row[0]
    #         print(bookurl)
    #         yield scrapy.Request(bookurl, meta={'bookurl': bookurl},callback=self.parse_detail)
    #
    # def parse_detail(self,response):
    #     item={}
    #     item['name'] = response.xpath('//h1/text()').extract_first()
    #     item['author'] =response.xpath('//div[@class="title"]/span/a/text()').extract_first()
    #     word_count =response.xpath('//p[@class="sub-data"]/span[1]/em/text()').extract_first()
    #     item['word_count'] = self.parseString(word_count)
    #     page_view = response.xpath('//p[@class="sub-data"]/span[2]/em/text()').extract_first()
    #     item['page_view'] =self.parseString(page_view)
    #     shoucang =response.xpath('//p[@class="sub-data"]/span[3]/em/text()').extract_first()
    #     item['shoucang'] = self.parseString(shoucang)
    #     item['lastupdate'] = response.xpath('//div[@class="sub-newest"]/p[1]/span[@class="time"]/text()').extract_first()
    #     item['spiderid'] = 'xxsy'
    #     item['url'] = response.meta['bookurl']
    #     item['category'] = re.search('类别：(.*?)<',response.text).group(1)
    #     item['yuepiao'] = response.xpath('//dl[@class="piao-detail"]/dd[1]/p[@class="nums"]/text()').extract_first()
    #     item['description']=response.xpath('string(//dl[@class="introcontent"]/dd)').extract_first()
    #     item['status'] ='连载中'
    #     item['biaoqian'] =','.join(response.xpath('//p[@class="sub-tags"]/a/text()').extract())
    #     item['banquan'] =''
    #     item['image'] =response.xpath('//dt/img/@src').extract_first()
    #     item['current_date'] = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    #     item['points'] = 0
    #     item['site'] = 'xxsy'
    #     item['haopingzhishu'] = '0.0'
    #     item['comment_count'] = 0
    #     item['redpack'] = 0
    #     item['yuepiaoorder'] = 0
    #     item['flower'] = 0
    #     item['diamondnum'] = 0
    #     item['coffeenum'] = 0
    #     item['eggnum'] = 0
    #     item['redpackorder'] = 0
    #     item['isvip'] = ''
    #     item['total_recommend'] = 0
    #     item['totalrenqi'] = 0
    #     item['hongbao'] = 0
    #     item['vipvote'] = 0
    #     item['review_count'] = 0
    #     item['printmark'] = 0
    #     yield item

    ################################
    def parse(self, response):
        # self._logger.debug("crawled url {}".format(response.request.url))
        pn = int(re.search('pn=(\d+)', response.url).group(1))
        if pn == 1:
            page_count = 1800
            for i in range(2, page_count + 1):
                next_page = re.sub('pn=1', 'pn=%d' % i, response.url)
                request = scrapy.Request(next_page, priority=100)
                request.meta['priority'] = -10
                yield request
        for node in response.xpath('//div[@class="result-list"]/ul/li'):
            try:
                item = {}
                item['spiderid'] = 'xxsy'
                item['url'] = "http://www.xxsy.net" + node.xpath('div[@class="info"]/h4/a/@href').extract_first()
                item['name'] = node.xpath('div[@class="info"]/h4/a/text()').extract_first()
                item['author'] = node.xpath('div[@class="info"]/h4/span/a[1]/text()').extract_first()
                values = node.xpath('div[@class="info"]/p[@class="number"]/span/text()').extract()
                # item['page_view'] = values[0].replace(u'总点击：','')
                item['word_count'] = int(values[3].replace(u'字数：', ''))
                item['lastupdate'] = values[2].replace('更新：', '')
                item['yuepiao'] = values[1].replace('月票：', '')
                item['category'] = node.xpath(
                    'div[@class="info"]/h4/span[@class="subtitle"]/a[2]/text()').extract_first()
                item['description'] = node.xpath('div[@class="info"]/p[@class="detail"]/text()').extract_first()
                # item['shoucang'] = int(node.xpath('li[@class="title"]/span[3]/text()').extract_first())
                item['status'] = node.xpath('div[@class="info"]/h4/span[@class="subtitle"]/span/text()').extract_first()
                item['banquan'] = ''  # node.xpath('li[@class="title"]/span[3]/text()').extract_first()

                item['biaoqian'] = node.xpath(
                    'div[@class="info"]/h4/span[@class="subtitle"]/a[3]/text()').extract_first()
                item['image'] = node.xpath('//a[@class="book commonbook"]/img/@src').extract_first()
                item['current_date'] = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                item['points'] = 0
                item['site'] = 'xxsy'
                item['haopingzhishu'] = '0.0'
                item['comment_count'] = 0
                item['redpack'] = 0
                item['yuepiaoorder'] = 0
                item['flower'] = 0
                item['diamondnum'] = 0
                item['coffeenum'] = 0
                item['eggnum'] = 0
                item['redpackorder'] = 0
                item['isvip'] = ''
                item['total_recommend'] = 0
                item['totalrenqi'] = 0
                item['hongbao'] = 0
                item['vipvote'] = 0
                item['review_count'] = 0
                item['printmark'] = 0
                req = scrapy.Request(item['url'], callback=self.parse_item, priority=2)
                req.meta['item'] = item
                req.meta['priority'] = 0
                yield req
            except Exception as e:
                print(e)
                # self._logger.error(e)

    def parse_item(self, response):
        item = response.meta['item']
        try:
            values = response.xpath('//p[@class="sub-data"]/span/em/text()').extract()
            item['page_view'] = self.parseString(values[1])
            item['shoucang'] = self.parseString(values[2])
            yield item
        except Exception as e:
            print(e)
            # self._logger.error(e)

    def parseString(self, strValue):
        result = 0
        # self._logger.debug(strValue)
        data = float(re.search('([\d.]+)', strValue).group(1))
        # self._logger.debug(data)
        if '万' in strValue:
            result = data * 10000
        elif '亿' in strValue:
            result = data * 100000000
        else:
            result = data
        return result

