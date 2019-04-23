# -*- coding: utf-8 -*-
import pymysql
import re
from crawling.items import SpiderNovelItem
import time
import sys
import json
import scrapy
import crawling.spiders.fileloader
import logging
from scrapy.utils.project import get_project_settings


class HxtxSpider(scrapy.Spider):
    name = "jjwxc"
    # download_delay = 1
    start_urls = [
        'http://app.jjwxc.org/search/getSearchForKeyWords?offset=0&limit=20&bq=0&fw=0&yc=0&xx=0&sd=0&lx=0&fg=0&mainview=0&fbsj=0&isfinish=0&sortType=0']
    # custom_settings = {
    #     "DOWNLOADER_MIDDLEWARES": {
    #         # 'crawling.middleware.CookiesMiddleware' :400,
    #         'crawling.middleware.PcUserAgentMiddleware': 401,
    #     },
    #     "REFERER_ENABLED": False,
    #     "DOWNLOAD_DELAY": 0.25
    # }

    #
    def parse(self, response):
        try:
            if re.search('offset=0&', response.url):
                for page in range(1,5000):
                    offset = page * 20
                    next_page = re.sub('offset=0&', 'offset=%d&' % offset, response.url)
                    request = scrapy.Request(next_page, callback=self.parse)
                    request.meta['priority'] = -10
                    yield request
            items = json.loads(response.body_as_unicode())
            for item in items['items']:
                novelid = item['novelid']
                request = scrapy.Request('http://app.jjwxc.org/androidapi/novelbasicinfo?novelId=%s' % novelid,
                                         callback=self.book_details)
                request.meta['priority'] = 0
                yield request
        except Exception as e:
            logging.error(e)

    ##### 补抓
     # def start_requests(self):
     #
     #
     #     import pandas as pd
     #     bookurls = pd.read_csv('D:/hulian/spiders/novelspiders/crawling/jj09281.csv')
     #     for bookid in bookurls['id']:
     #         novelid = re.search('(\d+)',bookid).group(1)
     #         yield scrapy.Request('http://app.jjwxc.org/androidapi/novelbasicinfo?novelId=%s' % novelid,
     #                        callback=self.book_details)


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
    #         'SELECT url FROM rawdata WHERE crawldate = "2018-11-28" AND site ="jjwxc" AND page_view>20000 and word_count>15000 AND `url` not in (SELECT `url` FROM rawdata WHERE crawldate = "2018-12-30")'
    #     )
    #
    #     rows = cursor.fetchall()
    #     for row in rows:
    #         bookurl = row[0]
    #         print(bookurl)
    #         novelid = re.search('novelid=(\d+)', bookurl).group(1)
    #         yield scrapy.Request('http://app.jjwxc.org/androidapi/novelbasicinfo?novelId=%s' % novelid, meta={'bookurl': bookurl}, callback=self.book_details)
    ####
    # def start_requests(self):
    #     bookurl='http://www.jjwxc.net/onebook.php?novelid=1984011'
    #     novelid = re.search('novelid=(\d+)',bookurl).group(1)
    #     yield scrapy.Request('http://app.jjwxc.org/androidapi/novelbasicinfo?novelId=%s' % novelid, meta={'bookurl': bookurl}, callback=self.book_details)

    def book_details(self, response):

        novel = json.loads(response.body_as_unicode())
        item = {}
        item['spiderid'] = 'jjwxc'
        # item['spiderid'] = response.meta['spiderid']
        # item['url'] = response.url
        item['name'] = novel['novelName']
        item['url'] = 'http://www.jjwxc.net/onebook.php?novelid=%s' % novel['novelId']
        item['author'] = novel['authorName']
        item['category'] = novel['novelClass']
        description = novel['novelIntro']
        item['description'] = re.sub('&lt;br/&gt;', '', description)[:2000]
        item['yuepiao'] = 0
        item['shoucang'] = 0
        item['hongbao'] = 0
        item['biaoqian'] = novel['novelTags']
        item['haopingzhishu'] = '0.0'
        item['total_recommend'] = 0
        item['review_count'] = 0
        item['printmark'] = 0
        item['status'] = novel['series']
        item['pubtime'] = ''
        item['points'] = self.parse2Int(novel['novelScore'])
        item['comment_count'] = self.parse2Int(novel['comment_count'])
        item['shoucang'] = self.parse2Int(novel['novelbefavoritedcount'])
        item['word_count'] = self.parse2Int(novel['novelSize'])
        item['lastupdate'] = novel['renewDate']
        item['image'] = novel['novelCover']
        item['current_date'] = time.strftime(
            '%Y-%m-%d', time.localtime(time.time()))
        item['site'] = "jjwxc"
        item['redpack'] = 0
        item['yuepiaoorder'] = 0
        item['flower'] = 0
        item['diamondnum'] = 0
        item['coffeenum'] = 0
        item['eggnum'] = 0
        item['redpackorder'] = 0
        item['totalrenqi'] = 0
        item['vipvote'] = 0
        item['isvip'] = novel['isVip']
        item['banquan'] = '未签约' if novel['novelStep'] == 2 else '已签约'
        item['page_view'] = self.parse2Int(novel['novip_clicks'])

        yield item

    def parse2Int(self, str):
        if str is None or str == '':
            return 0
        str = str.replace(',', '')
        return int(str)