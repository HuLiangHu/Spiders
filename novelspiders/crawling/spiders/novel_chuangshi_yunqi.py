# -*- coding: utf-8 -*-
import time

import pymysql
from crawling.items import SpiderNovelItem
# from redis_spider import scrapy.Spider
import re
import sys
import json
import scrapy
import crawling.spiders.fileloader
# reload(sys)
# sys.setdefaultencoding('utf-8')
from scrapy.utils.project import get_project_settings


class ChuangshiSpider(scrapy.Spider):
    name = "chuangshi_yunqi"
    # download_delay = 5
    start_urls = ['http://chuangshi.qq.com/bk/so1/p/{}.html',
                  'http://yunqi.qq.com/bk/so1/n30p{}'
                  ]
    custom_settings = {
        # "COOKIES_ENABLED": True,
        # "COOKIES_DEBUG": True,
        "REFERER_ENABLED": True,
        "DEFAULT_REQUEST_HEADERS" : {
            'Referer': 'http://chuangshi.qq.com'

        }
    }
    headers ={
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36 '
    }
    def parse(self, response):
        '''
        try:
            self._logger.debug("crawled url {}".format(response.request.url))
            urls = fileloader.loadurls()
            for url in urls:
                request = scrapy.Request(url, callback=self.parse_item,priority = 2)
                yield request
        except Exception as e:
            self._logger.error(e.message)
        '''

        for i in range(1,1000):
        # for i in range(2, 4):
            url = self.start_urls[1].format(i)
            request =  scrapy.Request(url, callback=self.parse,priority = 100)
            request.meta['priority'] = -10
            request.meta['retry_times'] = 3
            yield request

        for i in range(1,500):
        # for i in range(2, 5):
            url = self.start_urls[0].format(i)
            request =  scrapy.Request(url, callback=self.parse,priority = 100)
            request.meta['priority'] = -10
            request.meta['retry_times'] = 3
            yield request

        # for yunqi
        # for each in response.xpath('//div[@id="pageHtml2"]/a/@href').extract():
        #     request =  scrapy.Request(each, callback=self.parse,priority = 100)
        #     request.meta['priority'] = -10
        #     request.meta['retry_times'] = 3
        #     yield request

        for each in response.xpath('//div[@id="detailedBookList"]/div/a/@href').extract():
            request = scrapy.Request(each, callback=self.parse_item,priority = 2)
            request.meta['priority'] = 0
            yield request
        # for chuangshi
        for each in response.xpath('//td/a[@class="green"]/@href').extract():
            request = scrapy.Request(each, callback=self.parse_item,priority = 2)
            request.meta['priority'] = 0
            yield request
        # for each in response.xpath('//a[@class="nextBtn"]/@href').extract():
        #     request = scrapy.Request(each, callback=self.parse,priority = 100)
        #     request.meta['priority'] = -10
        #     request.meta['retry_times'] = 3
        #     yield request
    def start_requests(self):
        settings = get_project_settings()
        conn = pymysql.connect(
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            db=settings['MYSQL_DBNAME'],
            host=settings['MYSQL_HOST'],
            charset="utf8",
            use_unicode=True
        )
        cursor = conn.cursor()
        cursor.execute(
            'SELECT url FROM rawdata WHERE crawldate = "2018-11-28" AND site ="yunqi" AND page_view>20000 and word_count>15000 AND url not in (SELECT url FROM rawdata WHERE crawldate = "2018-12-30")'
        )

        rows = cursor.fetchall()
        for row in rows:
            bookurl = row[0]
            print(bookurl)
            yield scrapy.Request(bookurl, meta={'bookurl': bookurl}, callback=self.parse_item)



    def parse_item(self, response):
        item = {}
        if '小说不存在!' in response.text:
            print(print('Not Find This Book:',response.url))
        else:
            item['spiderid'] = 'chuangshi_yunqi'
            item['url'] = response.url
            item['name'] = response.xpath(
                '//div[@class="main2"]/div/div[3]/strong/a/text()').extract_first()
            item['author'] = response.xpath(
                '//div[@class="au_name"]/p[2]/a/text()').extract_first()

            item['category'] = response.xpath(
                '//div[@class="main2"]/div/div[3]/a[3]/text()').extract_first()
            item['description'] = ''
            if len(response.xpath('//div[@class="info"]/p/text()').extract()) != 0:
                for each in response.xpath('//div[@class="info"]/p/text()').extract():
                    item['description'] = item['description'] + each
            item['description'] = item['description'][:255]
            search_result = re.search(
                '点击：(\d+)</td><td>总人气：(\d+)</td><td>周人气：\d+</td><td>总字数：(\d+)</td>',
                response.text)
            if search_result:
                item['page_view'] = int(search_result.group(1))
                item['totalrenqi'] = int(search_result.group(2))
                item['word_count'] = int(search_result.group(3))
            else:
                item['page_view'] = 0
                item['totalrenqi'] = 0
                item['word_count'] = 0
            item['points'] = 0
            item['status'] = response.xpath(
                '//div[@class="main1"]/div[1]/i[2]/text()').extract_first()
            search_result2 = re.search(
                '<td>月点击：\d+</td><td>月人气：\d+</td><td>月推荐：(\d+)</td>',
                response.text)
            if search_result2:
                item['yuepiao'] = int(search_result2.group(1))
            else:
                item['yuepiao'] = 0
            item['biaoqian'] = ''
            if len(response.xpath('//div[@class="tags"]/text()').extract()) != 0:
                for each in response.xpath('//div[@class="tags"]/text()').extract_first().split('：')[1].strip().split('、'):
                    item['biaoqian'] = item['biaoqian'] + each + ','
            item['lastupdate'] = ''
            if len(response.xpath('//*[@id="newChapterList"]/div[1]/text()').extract()) != 0:
                item['lastupdate'] = \
                    response.xpath(
                        '//*[@id="newChapterList"]/div[1]/text()').extract_first().split('：')[1].split(' ')[0]
            # else:
            #     item['lastupdate']=''

            item['image'] = response.xpath(
                '//a[@class="bookcover"]/img/@src').extract_first()
            item['current_date'] = time.strftime(
                '%Y-%m-%d', time.localtime(time.time()))
            # item['site'] = 'chuangshi'
            item['haopingzhishu'] = '0.0'
            item['redpack'] = 0
            item['yuepiaoorder'] = 0
            item['flower'] = 0
            item['diamondnum'] = 0
            item['coffeenum'] = 0
            item['eggnum'] = 0
            item['redpackorder'] = 0
            item['isvip'] = ''
            item['total_recommend'] = 0
            # item['totalrenqi'] = 0
            item['hongbao'] = 0
            item['vipvote'] = 0
            item['shoucang'] = 0
            item['review_count'] = 0
            item['printmark'] = 0
            item['banquan'] = ''
            bookid = re.search('\/(\d+)\.html',response.url).group(1)
            if re.match('^(http|https|ftp)\://chuangshi.qq.com/.*', response.url):
                item['site'] = 'chuangshi'
            elif re.match('^(http|https|ftp)\://yunqi.qq.com/.*', response.url):
                item['site'] = 'yunqi'
            else:
                item['site'] = ''

            # yield item

            if 'chuangshi.qq' in response.url:
                self.headers['referer'] = response.url
                yield scrapy.Request('http://chuangshi.qq.com/novelcomment/index.html?bid=%s' % bookid, callback=self.parse_comment,meta={'item':item},headers=self.headers)
            else :

                self.headers['referer'] = response.url
                # print(self.headers)
                yield scrapy.Request('http://yunqi.qq.com/novelcomment/index.html?bid=%s' % bookid, callback=self.parse_comment,meta={'item':item},headers=self.headers)


    def parse_comment(self, response):
        #print(response.text)
        item = response.meta['item']
        try:
            item['comment_count'] = int(json.loads(response.text)['data']['commentNum'])
            yield item
        except Exception as e:
            print(e)
            print('Not Find This Book:',item['url'])


