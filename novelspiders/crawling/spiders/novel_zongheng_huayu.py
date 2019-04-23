# encoding: utf-8
import json

import pymysql
from crawling.items import SpiderNovelItem
import time
import re
import scrapy
import crawling.spiders.fileloader
from scrapy.utils.project import get_project_settings


class ZonghengSpider(scrapy.Spider):
    name = "zongheng_huayu"
    # download_delay = 1
    start_urls = ['http://book.zongheng.com/store/c0/c0/b0/u4/p1/v9/s9/t0/ALL.html', #男
                  #'http://book.zongheng.com/store/c0/c0/b1/u1/p1/v9/s9/t0/ALL.html' #女
                  ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url,dont_filter=True)
    def parse(self, response):

        max_page = response.xpath('//div[starts-with(@class,"page")]/a[last()-1]/@page').extract_first()

        # if float(max_page)>200:
        #     max_page = 2000
        for i in range(1,200):
            next_page = re.sub('\/p\d+\/', '/p%d/' % i, response.url)
            request = scrapy.Request(next_page, callback=self.parse_item, priority=100)
            request.meta['priority'] = -10
            yield request

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
    #         'SELECT url FROM rawdata WHERE crawldate = "2018-11-28" AND site ="zongheng" AND page_view>20000 and word_count>15000 AND `name` not in (SELECT `name` FROM rawdata WHERE crawldate = "2018-12-30")'
    #     )
    #
    #     rows = cursor.fetchall()
    #     for row in rows:
    #         bookurl = row[0]
    #         print(bookurl)
    #         yield scrapy.Request(bookurl, meta={'bookurl': bookurl}, callback=self.book_details_zongheng)


    def parse_item(self, response):
            if 'c0/c0/b0/u4' in response.url:
                for bookurl in response.xpath('//div[@class="bookname"]/a/@href').extract():

                    shoucangs = response.xpath('//div[@class="bookilnk"]/span[2]').extract()
                    for shoucang in shoucangs:
                        shoucang = re.search('总收藏 (\d+)',shoucang).group(1)
                        yield scrapy.Request(bookurl, callback=self.book_details_zongheng, priority=2,meta={'shoucang':shoucang})
            else:
                for each in response.xpath('//div[@class="bookname"]/a/@href').extract():
                    bookurl ='http://huayu.baidu.com/book/{}.html'.format(re.search('(\d+)', each).group(1))

                    yield scrapy.Request(bookurl, callback=self.book_details_huayu, priority=2)

######
    #测试
    # def start_requests(self):
    #     bookurl ='http://huayu.baidu.com/book/454178.html'
    #     yield scrapy.Request(bookurl, callback=self.book_details_huayu, priority=2)
######


    #####
    # def start_requests(self):
    #     """
    #            补抓代码
    #            :return:
    #            """
    #     import pandas as pd
    #     bookurls = pd.read_csv('D:/hulian/spiders/novelspiders/crawling/17k.csv')
    #     for bookurl in bookurls['url']:
    #         yield scrapy.Request(bookurl, meta={'bookurl': bookurl}, callback=self.book_details_zongheng, priority=2)

    def book_details_huayu(self, response):
        try:
            item = {}
            item['spiderid'] = 'zongheng_huayu'
            item['url'] = response.url
            item['name'] = response.xpath('//div[@class="booktitle"]/div/h1/a/text()').extract_first()
            item['author'] = response.xpath('//div[@class="booktitle"]/div/h1/span/a/text()').extract_first()
            item['category'] = response.xpath('//div[@class="loca title"]/a[3]/text()').extract_first()
            item['page_view'] = float(response.xpath('//div[@class="booknumber"]/text()').extract()[1].strip())
            item['comment_count'] = float(response.xpath('//span[@class="total_threads"]/text()').extract_first())
            item['word_count'] = float(response.xpath('//div[@class="booknumber"]/text()').extract()[2].strip())
            item['description'] = ''
            if len(response.xpath('//p[@class="jj"]/text()').extract()) != 0:
                for each in response.xpath('//p[@class="jj"]/text()').extract():
                    item['description'] = item['description'] + each
            item['description'] = item['description'][:255]
            item['pofloats'] = float(response.xpath('//div[@class="booknumber"]/text()').extract()[4].strip())
            item['banquan'] = ''
            if len(response.xpath('//div[@class="booktitle"]/div/h1/b/text()').extract()) != 0:
                item['banquan'] = response.xpath('//div[@class="booktitle"]/div/h1/b/text()').extract_first()
            item['yuepiao'] = 0
            item['yuepiaoorder'] = 0
            item['flower'] = 0
            item['diamondnum'] = 0
            item['coffeenum'] = 0
            item['eggnum'] = 0
            item['redpack'] = 0
            item['redpackorder'] = 0
            item['isvip'] = ''
            item['points'] = response.xpath('//div[@class="booknumber"]/text()').extract()[4].strip()
            item['shoucang'] = 0
            item['haopingzhishu'] = '0.0'
            item['total_recommend'] = 0
            item['totalrenqi'] = 0
            item['hongbao'] = 0
            item['vipvote'] = 0
            item['review_count'] = 0
            item['prfloatmark'] = 0
            item['printmark'] = 0
            item['lastupdate'] = response.xpath('//div[@class="booknumber"]/text()').extract()[5].strip()
            item['status'] = ''
            if response.xpath('//div[@class="booktitle"]/div[2]/@class').extract_first() == 'lzz':
                item['status'] = '连载中'
            if response.xpath('//div[@class="booktitle"]/div[2]/@class').extract_first() == 'ywj':
                item['status'] = '已完结'
            item['biaoqian'] = ''
            if len(response.xpath('//div[@class="wz"]/p[2]/a/text()').extract()) != 0:
                for each in response.xpath('//div[@class="bookinfo"]/div[2]/p[2]/a/text()').extract():
                    item['biaoqian'] = item['biaoqian'] + each + ','
            item['image'] = response.xpath('//div[@class="img"]/a/img/@src').extract_first()
            item['current_date'] = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            item['site'] = 'huayu'

            yield item
        except Exception as e:
            self.logger.error(e)

    def book_details_zongheng(self, response):
        if response.status == 200:

            item = {}
            item['spiderid'] = 'zongheng_huayu'
            item['url'] = response.url
            item['name'] = str(response.xpath('//div[@class="book-name"]/text()').extract_first()).strip()
            item['author'] = response.xpath('//div[@class="au-name"]/a/text()').extract_first()
            item['category'] = response.xpath('//div[@class="tabA-float cate-cell"]/ul/li/a/text()').extract_first()
            if len(response.xpath('//div[@class="nums"]/span[3]/i/text()').extract()) != 0:
                item['page_view'] = self.parseString(
                    response.xpath('//div[@class="nums"]/span[3]/i/text()').extract_first().strip())
            else:
                item['page_view'] = 0
            if len(response.xpath('//div[@class="nums"]/span[2]/i/text()').extract()) != 0:
                item['total_recommend'] = self.parseString(
                    response.xpath('//div[@class="nums"]/span[2]/i/text()').extract_first().strip())
            else:
                item['total_recommend'] = 0

            item['word_count'] = self.parseString(
                response.xpath('//div[@class="nums"]/span[1]/i/text()').extract_first())
            item['description'] = ''
            if len(response.xpath('//div[@class="book-dec Jbook-dec hide"]/p/text()').extract()) != 0:
                for each in response.xpath('//div[@class="book-dec Jbook-dec hide"]/p/text()').extract():
                    item['description'] = item['description'] + each
            item['description'] = item['description'][:255]
            item['points'] = 0
            try:
                item['yuepiao'] = int(response.xpath('//div[@class="fr rank-r"]/span[2]/i/text()').extract_first())
            except:
                item['yuepiao'] = 0

            item['shoucang'] = response.meta['shoucang']
            item['status'] = response.xpath('//div[@class="book-label"]/a[1]/text()').extract_first()
            item['image'] = response.xpath('//div[@class="book-img fl"]/img/@src').extract_first()
            item['current_date'] = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            item['site'] = 'zongheng'
            item['haopingzhishu'] = '0.0'
            item['redpack'] = 0
            item['yuepiaoorder'] = 0
            item['flower'] = 0
            item['diamondnum'] = 0
            item['coffeenum'] = 0
            item['eggnum'] = 0
            item['redpackorder'] = 0
            item['isvip'] = ''
            item['banquan'] = ''
            item['totalrenqi'] = 0
            item['lastupdate'] = ''
            item['hongbao'] = 0
            item['biaoqian'] = ''
            item['vipvote'] = 0
            item['review_count'] = 0
            item['printmark'] = 0
            bookid = re.search('(\d+)',item['url']).group(1)
            commenturl = 'http://forum.zongheng.com/api/forums/postlist?&bookId={0}&forumType=4&mark=&_={1}'.format(bookid,int(time.time()*1000))

            yield scrapy.Request(commenturl,meta={'item':item},callback=self.parse_comment_count)

    def parse_comment_count(self,response):
        item = response.meta['item']
        item['comment_count'] = json.loads(response.text)['data']['threadNum']
        yield item

    def parseString(self, strValue):
        if '万' in strValue:
            data = float(re.sub('万', '', strValue)) * 10000
        elif '亿' in strValue:
            data = float(re.sub('亿', '', strValue)) * 100000000

        else:
            data = int(strValue)
        return round(data)
