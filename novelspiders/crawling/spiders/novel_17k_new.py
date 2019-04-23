import time
# from redis_spider import scrapy.Spider
import pymysql
import re
import json
import scrapy
import sys

from scrapy.utils.project import get_project_settings


class Novel17knewSpider(scrapy.Spider):
    name = "17knew"
    #
    download_delay = 1
    start_urls = [
        "http://api.17k.com/v2/book?app_key=1351550300&sort_type=4&page=1&num=100&site=2&category_1=21&category_2=0"]
    # 21,24,3,22,23,14,(3,5),(3,17),(3,20),(3,18)
    # custom_settings = {
    #     "DOWNLOADER_MIDDLEWARES": {
    #         # 'crawling.middleware.CookiesMiddleware' :400,
    #         'crawling.middleware.PcUserAgentMiddleware': 401,
    #     }
    # }

    def __init__(self, *args, **kwargs):
        super(Novel17knewSpider, self).__init__(*args, **kwargs)

#####
    # def start_requests(self):
    #     for page in range(1,500):
    #         urls = [
    #                 'http://all.17k.com/lib/book/2_0_0_0_0_4_0_0_{}.html'.format(page),  # 男生版
    #                 'http://all.17k.com/lib/book/3_0_0_0_0_4_0_0_{}.html'.format(page),  # 女生版
    #                 'http://all.17k.com/lib/book/4_0_0_0_0_4_0_0_{}.html'.format(page)   # 个性化
    #                 ]
    #         for url in urls:
    #             yield scrapy.Request(url,callback=self.parse)
    # def parse(self, response):
    #     bookurls = response.xpath('//a[@class="jt"]/@href').extract()
    #     for bookurl in bookurls:
    #         if 'http' in bookurl:
    #             yield scrapy.Request(bookurl,meta={'bookurl':bookurl},callback=self.parse_item)

######

######补抓
    # def start_requests(self):
    #     import pandas as pd
    #     bookurls = pd.read_csv('D:/hulian/spiders/novelspiders/crawling/17kbookid.csv')
    #     for bookurl in bookurls['url']:
    #         try:
    #             yield scrapy.Request(bookurl, meta={'bookurl': bookurl}, callback=self.parse_item)
    #         except:
    #             with open('17k.txt','a') as f:
    #                 f.write(bookurl)
    #                 f.write('\n')
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
            'SELECT url FROM rawdata WHERE crawldate = "2018-11-28" AND site ="17k" AND page_view>20000 and word_count>15000 and url not in (SELECT url FROM rawdata WHERE crawldate = "2018-12-30")'
        )

        rows = cursor.fetchall()
        for row in rows:
            bookurl = row[0]
            print(bookurl)
            yield scrapy.Request(bookurl, meta={'bookurl': bookurl}, callback=self.parse_item)

#######


####测试
    # def start_requests(self):
    #     url = 'http://www.17k.com/book/2588297.html'
    #     yield scrapy.Request(url, meta={'bookurl': url}, callback=self.parse_item)
#####
    def parse_item(self, response):
        time.sleep(2)
        item = {}
        item['type'] = 'novel'
        item['spiderid'] = '17k'
        item['url'] = response.meta['bookurl']
        item['image'] = response.xpath('//div[@class="BookInfo"]/div/div/a/img/@src').extract_first()
        # item['word_count'] = int(novel['wordCount'])
        try:
            lastupdate= response.xpath('//dl[@class="NewsChapter"]//span[@class="time"]/text()').extract_first()
            item['lastupdate'] = re.search("更新时间：(.*)",lastupdate).group(1)
        except:
            item['lastupdate'] =None
        try:
            status =response.xpath('//div[@class="label"]/a/@title').extract_first()
            item['status'] = '连载' if '连载'in status else '完结'
        except:
            item['status'] = '连载'
        item['site'] = "17k"

        item['current_date'] = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        try:
            bookid = re.search('.*book/(\d+)', response.url).group(1)
            item['bookid'] = bookid
            # item['word_count'] =int(response.xpath('//div[@class="BookData"]/p[2]/em[@class="red"]/text()').extract_first())
            if len(response.xpath('//div[@class="BookData"]/p[2]/em[@class="red"]/text()').extract()) != 0:
                item['word_count'] = int(
                    response.xpath('//div[@class="BookData"]/p[2]/em[@class="red"]/text()').extract_first())
            else:
                item['word_count'] = 0
            item['name'] = response.xpath('//div[@class="BookInfo"]/div[2]/h1[1]/a/text()').extract_first()
            item['category'] = response.xpath('//div[@class="infoPath"]/div/a[3]/text()').extract_first()
            item['author'] = response.xpath('//div[@class="AuthorInfo"]/div/a[2]/text()').extract_first()
            item['description'] = ''

            if len(response.xpath('//div[@class="BookInfo"]/div[2]/dl/dd/div/a/text()').extract()) != 0:
                for each in response.xpath('//div[@class="BookInfo"]/div[2]/dl/dd/div/a/text()').extract():
                    item['description'] = item['description'] + each
            item['description'] = item['description'][:255]
            item['biaoqian'] = ''
            if len(response.xpath('//tr[@class="label"]/td/a/span/text()').extract()) != 0:
                for each in response.xpath('//tr[@class="label"]/td/a/span/text()').extract():
                    item['biaoqian'] = item['biaoqian'] + each + ','
            item['yuepiao'] = 0
            item['points'] = 0
            if len(response.xpath('//dl[@class="PiaoyouTop"]/dt/label[2]/span/text()').extract()) != 0:
                item['hongbao'] = int(
                    response.xpath('//dl[@class="PiaoyouTop"]/dt/label[2]/span/text()').extract_first().split('(')[
                        1].split(')')[0])
            else:
                item['hongbao'] = 0
            item['vipvote'] = 0
            if len(response.xpath('//dl[@class="PiaoyouTop"]/dt/label/span[@id="flower_total"]/text()').extract()) != 0:
                item['flower'] = int(
                    response.xpath(
                        '//dl[@class="PiaoyouTop"]/dt/label/span[@id="flower_total"]/text()').extract_first().replace(
                        '(', '').replace(')', ''))
            else:
                item['flower'] = 0

            item['image'] = response.xpath('//div[@class="BookInfo"]/div/div/a/img/@src').extract_first()
            if len(response.xpath('//span[@class="red"]/text()').extract()) != 0:
                item['banquan'] = response.xpath('//span[@class="red"]/text()').extract_first()
            else:
                item['banquan'] = ''
            time.sleep(1)
            #item['page_view'] =response.xpath('//em[@class="blue"]/text()').extract_first()
            #item['comment_count'] = response.xpath('//a[@id="comment_more1"]/span[@class="red"]/text()').extract_first()
            item['haopingzhishu'] = '0.0'
            item['redpack'] = 0
            item['yuepiaoorder'] = 0
            item['diamondnum'] = 0
            item['coffeenum'] = 0
            item['eggnum'] = 0
            item['redpackorder'] = 0
            item['isvip'] = ''
            item['total_recommend'] = 0
            item['review_count'] = 0
            item['totalrenqi'] = 0
            item['shoucang'] = 0
            item['pubtime'] =None
            # request = scrapy.Request("http://www.17k.com/bookservice/initbook.action?r=%s" % bookid,
            #                          callback=self.book_details_extra1, priority=3)
            # request.meta['item'] = item
            # request.meta['priority'] = 10
            try:
                yield scrapy.Request(
                    "http://api.17k.com/v2/book/{}/stat_info?app_key=3362611833&hb_info=1&flower_info=1&stamp_info=1&click_info=1".format(bookid),
                    meta={'item':item},callback=self.parse_item2)
            except:
                with open('17k.txt','a') as f:
                    f.write(response.meta['bookurl'])
                    f.write('\n')
        except Exception as e:
            self.logger.error(e)

    def parse_item2(self, response):
        # bookid = response.url.split('?')[1]
        try:
            stat_info = json.loads(response.text)['data']
            item = response.meta['item']
            # item['weekclickCount'] = stat_info['click_info']['week_count']
            # item['monthclickCount'] = stat_info['click_info']['month_count']
            item['page_view'] = stat_info['click_info']['total_count']
            item['hongbao'] = stat_info['hb_info']['total_count']
            item['flower'] = stat_info['flower_info']['total_count']
            item['printmark'] = stat_info['stamp_info']['total_count']
            url ='http://comment.17k.com/topic_list?commentType=all&order=1&bookId={}&page=1&pagesize=20&r=0.12946200186309653'.format(item['bookid'])
            yield scrapy.Request(url,meta={'item':item},callback=self.parse_item3)

        except Exception as e:
            self.logger.error(e)
    def parse_item3(self, response):
        item = response.meta['item']
        info = json.loads(response.text)
        item['comment_count'] =info['page']['count']

        yield item
