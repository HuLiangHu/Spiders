# -*- coding: utf-8 -*-
# __author__ = hul
# __date__ = 2018/9/30 上午11:36
import time
# from redis_spider import scrapy.Spider
import re
import json
import scrapy
import sys

from urllib.parse import urlencode
from scrapy.utils.project import get_project_settings
import pymysql


class HongXiuSpider(scrapy.Spider):
    name = "hongxiu"

    download_delay = 1
    #
    # custom_settings = {
    #     "DOWNLOADER_MIDDLEWARES": {
    #         # 'crawling.middleware.CookiesMiddleware' :400,
    #         'crawling.middleware.PcUserAgentMiddleware': 401,
    #     }
    #
    # }
    headers = {
        'Accept': 'application/json',
        'Cookie': 'appId=41; appTheme=default; areaId=4; channel=appstore; ywguid=0; ywkey=',
        'deviceInfo': '8m867iChUwKliGAHwaQIsLVCKV/Z4L8C5jirpMNe+PtkyzvybbTNThBPtbrbp1cryywi9dOMvgaJ2gl/lsNE0r2vRgc4xCILhLz3IMzbXzXhbVFZYgAnwyggcAEXsErqtAUnmxzPX+pxHHiVFeFOO1ooI4gPUC40b/g2xFRAv1Ke1gvAqxBQ3Q==',
        'User-Agent': 'readx/7.2.1 (iPhone; iOS 12.0; Scale/2.00)'
    }
    custom_settings= {
        'Accept': 'application/json',
        'Cookie': 'appId=41; appTheme=default; areaId=4; channel=appstore; ywguid=0; ywkey=',
        'deviceInfo': '8m867iChUwKliGAHwaQIsLVCKV/Z4L8C5jirpMNe+PtkyzvybbTNThBPtbrbp1cryywi9dOMvgaJ2gl/lsNE0r2vRgc4xCILhLz3IMzbXzXhbVFZYgAnwyggcAEXsErqtAUnmxzPX+pxHHiVFeFOO1ooI4gPUC40b/g2xFRAv1Ke1gvAqxBQ3Q==',
        'User-Agent': 'readx/7.2.1 (iPhone; iOS 12.0; Scale/2.00)'
    }

    def start_requests(self):
        page = 1
        for tagid in range(10001,10017):

            url ='https://appapi.hongxiu.com/api/v1/tag/list?tagId={0}&pageIndex={1}&pageSize=20&size=-1&orderBy=1&finishOrVip=-1&secondTagId=-1'.format(tagid,str(page))

            yield scrapy.Request(url, headers=self.headers,dont_filter=True,meta={'page':page})

    def parse(self, response):
        #print(json.loads(response.text))
        infos = json.loads(response.text)['data']
        for info in infos['items']:
            item = {}
            item['name'] = info['bookName']
            item['bookid'] = info['bookId']
            item['author'] = info['authorName']
            item['status'] = info['bookStatStr']
            item['word_count'] = info['wordsCnt']
            item['description'] = info['description']
            item['tag'] = ','.join(info['tags'])

            url = 'https://appapi.hongxiu.com/api/v1/book/info?bookId={}&screen=1'.format(item['bookid'])
            yield scrapy.Request(url,callback=self.parse_bookinfo1,meta={'item':item},headers=self.headers)
        next_page_flag = json.loads(response.text)['data']
        #print(next_page_flag['items'])
        if next_page_flag['items']:
            #print('='*20,'下一页','='*20)
            page = int(response.meta['page'])+1
            url = re.sub('pageIndex=\d+','pageIndex={}'.format(str(page)),response.url)
            #print(url)
            yield scrapy.Request(url,meta={'page':page},callback=self.parse,headers=self.headers)
    def parse_bookinfo1(self,response):
        item = response.meta['item']
        info = json.loads(response.text)['data']
        item['shoucang'] = info['bookInfo']['collectCount']
        lastupdate = info['bookInfo']['lastVipChapterTime']
        item['lastupdate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(lastupdate / 1000))
        isVip = str(info['bookInfo']['isVip'])
        if isVip =='1':
            item['isvip'] ='Vip'
        else:
            item['isvip'] ="免费"

        item['banquan'] = re.search('版权：(.*)', info['bookInfo']['copyright']).group(1)
        item['pubtime'] = re.search('(.*)上架', info['bookInfo']['copyright']).group(1)

        item['yuepiao'] = info['ticketInfo']['monthTicket']
        item['category'] = info['bookInfo']['categoryName']
        url = 'https://appapi.hongxiu.com/api/v1/book/info?bookId={}&screen=2'.format(item['bookid'])
        yield scrapy.Request(url,callback=self.parse_bookinfo2,meta={"item":item},headers=self.headers)
        # item['comment_count'] = info['commentInfo']['totalCount']
        #
    ######测试
    # def start_requests(self):
    #     url = 'https://www.hongxiu.com/book/11494991404547503'
    #     yield scrapy.Request(url, callback=self.parse_detail,dont_filter=True)
    #
    #
    # #######
    #     """
    #     补抓代码
    #     """
    #     def start_requests(self):
    #         file_name = '1010.txt'
    #         with open(file_name, 'r') as f:
    #             for i in f.readlines():
    #                 url = i.strip('\n')
    #                 yield scrapy.Request(url,callback=self.parse_detail)
    # ########
    #
    # #######
    #         """
    #         补抓代码
    #         """
    #     def start_requests(self):
    #         settings = get_project_settings()
    #         conn = pymysql.connect(
    #             user=settings['MYSQL_USER'],
    #             passwd=settings['MYSQL_PASSWD'],
    #             db=settings['MYSQL_DBNAME'],
    #             host=settings['MYSQL_HOST'],
    #             charset="utf8",
    #             use_unicode=True
    #         )
    #         cursor = conn.cursor()
    #         cursor.execute(
    #             'SELECT url FROM rawdata WHERE crawldate like "2017-06%" AND site ="hongxiu" AND page_view>20000 and word_count>15000 and url not in (SELECT url FROM rawdata WHERE crawldate LIKE "2018-10%")'
    #         )
    #
    #         rows = cursor.fetchall()
    #         for row in rows:
    #             bookurl = 'https://www.hongxiu.com/book/{}'.format(re.search('(\d+)',row[0]).group(1))
    #             print(bookurl)
    #             yield scrapy.Request(bookurl, meta={'bookurl': bookurl}, callback=self.parse_detail)

    ########

    def parse_bookinfo2(self, response):

        item = response.meta['item']
        item['comment_count'] = json.loads(response.text)['data']['commentInfo']['totalCount']

        url = 'https://www.hongxiu.com/book/{}'.format(item['bookid'])
        yield scrapy.Request(url, callback=self.parse_detail, meta={"item": item}, headers=self.headers)

    def parse_detail(self, response):
        if response.status == 200:
            item = response.meta['item']
            item['url'] = response.url
            page_view = response.xpath('//p[@class="total"]/span[3]/text()').extract_first()
            if '万' in response.xpath('//p[@class="total"]/em[3]').extract_first():
                item['page_view'] = int(float(page_view) * 10000)
            else:
                item['page_view'] = page_view

            item['current_date'] = time.strftime(
                '%Y-%m-%d', time.localtime(time.time()))
            item['pubtime'] = ''
            item['image'] =''
            item['points'] = 0
            item['yuepiaoorder'] = 0
            item['haopingzhishu'] = '0.0'
            item['redpack'] = 0
            item['flower'] = 0
            item['diamondnum'] = 0
            item['coffeenum'] = 0
            item['eggnum'] = 0
            item['redpackorder'] = 0
            item['totalrenqi'] = 0
            item['hongbao'] = 0
            item['vipvote'] = 0
            item['review_count'] = 0
            item['printmark'] = 0
            item['total_recommend'] = 0
            item['biaoqian'] =''
            item['site'] = 'hongxiu'
            yield item
    #         bookid = re.search('(\d+)', response.url).group(1)
    #         baseurl = 'https://www.hongxiu.com/ajax/comment/pageList?'
    #         parmas = {
    #             '_csrfToken': 'K447PYxrJoiPJxTcs18QFwzOtvjc9CcyNMDBQoVK',
    #             'pageNum': '1',
    #             'pageSize': '10',
    #             'bookId': bookid,
    #             '_': int(time.time() * 1000)
    #         }
    #         url = baseurl + urlencode(parmas)
    #         headers ={
    #             'Host': 'www.hongxiu.com',
    #             'Referer': 'https://www.hongxiu.com/book/{}'.format(item['bookid']),
    #             'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
    #         }
    #         yield scrapy.Request(url, meta={'item': item, 'bookid': bookid}, callback=self.parse_comment,headers=headers)
    #
    # def parse_comment(self, response):
    #     item = response.meta['item']
    #     """
    #     评论数
    #     :param response:
    #     :return:
    #     """
    #     info = json.loads(response.text)
    #     # item['author'] = info['data']['bookInfo']['author']
    #     # item['category'] = info['data']['bookInfo']['subCateName']
    #     item['comment_count'] = info['data']['total']
    #     yield item


