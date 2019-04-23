# -*- coding: utf-8 -*-
import time
# from redis_spider import scrapy.Spider
import re
import json
import scrapy
import sys
import crawling.spiders.fileloader


class Novel17kSpider(scrapy.Spider):
    name = "17k"
    #
    # download_delay = 1
    # start_urls=["http://api.17k.com/v2/book?app_key=1351550300&sort_type=4&page=1&num=100&site=0"]
    # 21,24,3,22,23,14,(3,5),(3,17),(3,20),(3,18)

    headers = {
        'Host': 'www.17k.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
    }

    def __init__(self, *args, **kwargs):
        super(Novel17kSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        for page in range(1, 550):
            url = 'http://api.17k.com/v2/book?app_key=1351550300&sort_type=4&page={}&num=100&site=0'.format(page)
            yield scrapy.Request(url)

    def parse(self, response):

        for info in json.loads(response.text)['data']:
            item = {}
            item['name'] = info['book_name']
            book_status = info['book_status']
            if book_status == '01':
                item['status'] = '连载中'
            else:
                item['status'] = '完结'
            item['description'] = info['intro']
            item['category'] = info['category_name_1'] + ',' + info['category_name_2']
            item['word_count'] = info['word_count']
            item['author'] = info['author_name']
            item['type'] = 'novel'
            item['spiderid'] = '17k'
            item['site'] = "17k"
            item['biaoqian'] = info['keyword']
            lastupdate = info['last_update_chapter_date']
            item['lastupdate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(lastupdate / 1000))
            isvip = info['book_free']
            if isvip == '1':
                item['isvip'] = '免费'
            else:
                item['isvip'] = 'VIP'
            item['current_date'] = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            item['image'] = info['cover']
            bookid = info['book_id']
            item['url'] = 'http://www.17k.com/book/%s.html' % bookid
            yield scrapy.Request(item['url'], callback=self.parse_book_details, meta={'item': item, 'bookid': bookid},
                                 headers=self.headers)

    def parse_book_details(self, response):

        try:
            item = response.meta['item']
            # if re.search('Q.bookid = (\d+);', response.text):
            #     bookid = re.search('Q.bookid = (\d+);', response.text).group(1)
            # else:
            #     bookid = re.search('book\/(\d+)\.html', response.url).group(1)
            # # item['word_count'] =int(response.xpath('//div[@class="BookData"]/p[2]/em[@class="red"]/text()').extract_first())
            # if len(response.xpath('//div[@class="BookData"]/p[2]/em[@class="red"]/text()').extract()) != 0:
            #     item['word_count'] =int(response.xpath('//div[@class="BookData"]/p[2]/em[@class="red"]/text()').extract_first())
            # else:
            #     item['word_count'] =0
            # item['name'] = response.xpath('//div[@class="BookInfo"]/div[2]/h1[1]/a/text()').extract_first()
            # item['category'] = response.xpath('//div[@class="infoPath"]/div/a[3]/text()').extract_first()
            # item['author'] = response.xpath('//div[@class="AuthorInfo"]/div/a[2]/text()').extract_first()
            # item['description'] = ''
            #
            # if len(response.xpath('//div[@class="BookInfo"]/div[2]/dl/dd/div/a/text()').extract()) != 0:
            #     for each in response.xpath('//div[@class="BookInfo"]/div[2]/dl/dd/div/a/text()').extract():
            #         item['description'] = item['description'] + each
            # item['description'] = item['description'][:255]
            # item['biaoqian'] = ''
            # if len(response.xpath('//tr[@class="label"]/td/a/span/text()').extract()) != 0:
            #     for each in response.xpath('//tr[@class="label"]/td/a/span/text()').extract():
            #         item['biaoqian'] = item['biaoqian'] + each + ','
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

            if len(response.xpath('//span[@class="red"]/text()').extract()) != 0:
                item['banquan'] = response.xpath('//span[@class="red"]/text()').extract_first()
            else:
                item['banquan'] = ''

            item['haopingzhishu'] = '0.0'
            item['redpack'] = 0
            item['yuepiaoorder'] = 0
            item['diamondnum'] = 0
            item['coffeenum'] = 0
            item['eggnum'] = 0
            item['redpackorder'] = 0
            item['total_recommend'] = 0
            item['review_count'] = 0
            item['totalrenqi'] = 0
            item['shoucang'] = 0
            request = scrapy.Request("http://www.17k.com/bookservice/initbook.action?r=%s" % response.meta['bookid'],
                                     callback=self.book_details_extra1, priority=3)
            request.meta['item'] = item
            request.meta['priority'] = 10
            yield request
        except Exception as e:
            self.logger.error(e)

    def book_details_extra1(self, response):
        try:
            bookid = re.search('r=(\d+)', response.url).group(1)
            signInCount = json.loads(response.text)
            item = response.meta['item']
            item['bookSignInCount'] = int(signInCount['count'])

            request = scrapy.Request("http://comment.17k.com/topic_list?bookId=%s" % bookid,
                                     callback=self.book_details_extra2, priority=2)
            request.meta['item'] = item
            request.meta['bookid'] = bookid
            request.meta['priority'] = 40
            yield request
        except Exception as e:
            self.logger.error(e)

    def book_details_extra2(self, response):
        # bookid = response.url.split('?')[1]
        try:
            comment = json.loads(response.text)
            item = response.meta['item']
            item['comment_count'] = int(comment['page']['count'])
            bookid = response.meta['bookid']
            request = scrapy.Request(
                "http://api.17k.com/v2/book/%s/stat_info?app_key=3362611833&hb_info=1&flower_info=1&stamp_info=1&click_info=1" % bookid,
                callback=self.book_details_extra3, priority=1)
            request.meta['item'] = item
            request.meta['priority'] = 50
            yield request
        except Exception as e:
            self.logger.error(e)

    def book_details_extra3(self, response):
        # bookid = response.url.split('?')[1]
        try:
            stat_info = json.loads(response.text)['data']
            item = response.meta['item']
            item['weekclickCount'] = stat_info['click_info']['week_count']
            item['monthclickCount'] = stat_info['click_info']['month_count']
            item['page_view'] = stat_info['click_info']['total_count']
            item['hongbao'] = stat_info['hb_info']['total_count']
            item['flower'] = stat_info['flower_info']['total_count']
            item['printmark'] = stat_info['stamp_info']['total_count']
            yield item
        except Exception as e:
            self.logger.error(e)