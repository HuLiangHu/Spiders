# -*- coding: utf-8 -*-
import json
import pymysql
import re
import requests
import scrapy
import os
import time
from fontTools.ttLib import TTFont, BytesIO
from scrapy.http.cookies import CookieJar
from scrapy.utils.project import get_project_settings
from urllib.parse import urlencode

# from novelspiders.crawling.items import SpiderNovelItem
#

class QidianSpider(scrapy.Spider):
    name = 'qidian'
    allowed_domains = ['qidian.com']
    start_urls = ['https://book.qidian.com/']
    custom_setting = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie':'hiijack=0; e1=%7B%22pid%22%3A%22qd_P_all%22%2C%22eid%22%3A%22%22%2C%22l1%22%3A5%7D; e2=%7B%22pid%22%3A%22qd_P_all%22%2C%22eid%22%3A%22%22%7D; _csrfToken=X0cCVcAVOjSLZbD6UsmLV2qh7gApfFLnxSxvd1xA; newstatisticUUID=1534489522_183988696; pgv_pvi=1957447680; pgv_si=s2120909824; focusGame=1; e1=%7B%22pid%22%3A%22qd_P_all%22%2C%22eid%22%3A%22%22%7D; e2=%7B%22pid%22%3A%22qd_P_all%22%2C%22eid%22%3A%22qd_C44%22%2C%22l1%22%3A5%7D',
        'Host': 'book.qidian.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        'Referer':'https://www.qidian.com/rank/yuepiao'
    }

    def __init__(self):
        self.max_page = 0
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
        }
        self.num_map = {'period': '.', 'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5',
                        'six': '6', 'seven': '7', 'eight': '8', 'nine': '9'}
#####
    def start_requests(self):

        baseurls = [
                   'https://www.qidian.com/all?orderId=8&style=1&pageSize=20&siteid=1&pubflag=0&hiddenField=0&page={}',  #男生版
                   'https://www.qidian.com/mm/all?orderId=8&style=1&pageSize=20&siteid=0&pubflag=0&hiddenField=0&page={}',#女生版
                   #'https://www.qidian.com/all_pub?orderId=8&style=1&pageSize=20&siteid=0&pubflag=0&hiddenField=0&page={}'
        ]
        #baseurl='https://www.qidian.com/all?orderId=8&style=1&pageSize=20&siteid=1&pubflag=0&hiddenField=0&page={}'
        for baseurl in baseurls:
            pageurls =[]
            for page in range(0,3000):#3000
                pageurl = baseurl.format(page)
                pageurls.append(pageurl)
                for url in pageurls:
                    yield scrapy.Request(url)

    def parse(self, response):
        bookurllist = response.xpath('//div[@class="book-mid-info"]/h4/a/@href').extract()

        #yuepiao = response.xpath('//*[@id="rank-view-list"]/div/ul/li/div[3]/div/p/span/span').extract()
        #yuepiaoorder = response.xpath('//span[starts-with(@class,"rank-tag no")]/text()').extract()
        #lastupdate = response.xpath('//*[@id="rank-view-list"]/div/ul/li/div[2]/p[3]/span/text()').extract()
        for i, bookurl in enumerate(bookurllist):
            bookurl = 'https:' + bookurl

            yield scrapy.Request(bookurl, meta={'bookurl': bookurl, 'cookiejar': 1},
                                 callback=self.detail_parse)
########


######
    # def start_requests(self):
    #     """
    #     补抓代码
    #     :return:
    #     """
    #     import pandas as pd
    #     bookurls = pd.read_csv('D:/hulian/spiders/novelspiders/crawling/qidian.csv')
    #     for bookurl in bookurls['url']:
    #         yield scrapy.Request(bookurl, meta={'bookurl': bookurl, 'cookiejar': 1},
    #                             callback=self.detail_parse)
    #
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
    #         'SELECT url FROM rawdata WHERE crawldate = "2019-01-30" AND site ="qidian" AND page_view>20000 and word_count>15000 AND url not in (SELECT url FROM rawdata WHERE crawldate = "2019-02-28")'
    #     )
    #
    #     rows = cursor.fetchall()
    #     for row in rows:
    #         bookurl = row[0]
    #         print(bookurl)
    #         yield scrapy.Request(bookurl, meta={'bookurl': bookurl}, callback=self.detail_parse)
    # #
    #

#####

####测试
    # def start_requests(self):
    #     #url ='https://book.qidian.com/info/1011945843'
    #     url ='https://book.qidian.com/info/1012053619'
    #     yield scrapy.Request(url, meta={'bookurl':url, 'cookiejar': 1},
    #                             callback=self.detail_parse)
#####


    def detail_parse(self, response):
        if '抱歉，页面无法访问' in response.text:
            print('Not Find This Book:',response.url)
        else:
            #获得cookie值，拿到Token
            Cookie = response.headers.getlist('Set-Cookie')[0].decode()  # 查看一下响应Cookie，也就是第一次访问注册页面时后台写入浏览器的Cookie
            cookies =Cookie.split(';')
            #print(cookies)
            cookies = (cookie.split('=', 1) for cookie in cookies)
            cookie = dict(cookies)
            _csrfToken =cookie['_csrfToken']
            # print(_csrfToken)
            # print(response.meta['bookurl'])
            font = None
            font_file = response.xpath('/html/body/div[2]/div[6]/div[1]/div[2]/p[3]').re_first(
                r'qidian\.gtimg\.com\/qd_anti_spider\/(\w+\.ttf)')
            # print(font_file)
            if font_file:
                font = self.create_font(font_file)
            item = {}


            item['name'] = response.xpath('//div[@class="book-info "]/h1/em/text()').extract_first()
            author = response.xpath('//div[@class="book-info "]/h1/span/a/text()').extract_first()  # 男生女生版
            if author:
                item['author'] =author
            else:
                item['author'] = response.xpath('//div[@class="book-info "]/h1/span/text()').extract_first()  # 出版

                item['grade'] =response.xpath('//h4[@id="j_bookScore"]/text()').extract_first()
            yuepiao =response.xpath('//i[@id="monthCount"]/text()').extract_first() #出版物
            if yuepiao:
                item['yuepiao'] =response.xpath('//i[@id="monthCount"]/text()').extract_first() #男生女生
            else:
                item['yuepiao'] =response.xpath('//i[@id="recCount"]/text()').extract_first() #出版物

            # yuepiao = response.meta['yuepiao']
            # yuepiao = self.modify_data(yuepiao, font)
            # # print(yuepiao)
            # # item['yuepiao'] = re.search('\d+', yuepiao).group(0)
            # item['yuepiaoorder'] = response.meta['yuepiaoorder']
            pattern = re.compile('</style><span.*?>(.*?)</span>', re.S)
            #  获取当前页面所有被字数字符
            numberlist = re.findall(pattern, response.text)
            reg = re.compile('<style>(.*?)\s*</style>', re.S)
            fonturl = re.findall(reg, response.text)[0]
            url = re.search('woff.*?url.*?\'(.+?)\'.*?truetype', fonturl).group(1)
            cmap = self.get_font(url)
            num_list = []
            for a in numberlist:
                num_list.append(self.get_encode(cmap, a))


            item['word_count'] = num_list[0] + \
                                 response.xpath('//div[@class="book-info "]//p/cite[1]/text()').extract_first()
            word_count = re.search('(.*)字', item['word_count']).group(1)

            if r'万' in word_count:
                item['word_count'] = float(word_count.replace(r'万', '')) * 10000
            elif r'亿' in word_count:
                item['word_count'] = float(word_count.replace(r'亿', '')) * 100000000
            else:
                item['word_count']=word_count

            page_view= num_list[1] + \
                                response.xpath('//div[@class="book-info "]//p/cite[2]/text()').extract_first()

            page_view = re.search('(.*)阅文总点击', page_view).group(1)
            if r'万' in page_view:
                item['page_view'] = float(page_view.replace(r'万', '')) * 10000
            elif r'亿' in page_view:
                item['page_view'] = float(page_view.replace(r'亿', '')) * 100000000
            else:
                item['page_view']=page_view
            try:
                item['total_recommend'] = num_list[3] +response.xpath('//div[@class="book-info "]//p/cite[4]/text()').extract_first()

                total_recommend = re.search('(.*)总推荐', item['total_recommend']).group(1)
                if r'万' in total_recommend:
                    item['total_recommend'] = float(total_recommend.replace(r'万', '')) * 10000
                elif r'亿' in total_recommend:
                    item['total_recommend'] = float(total_recommend.replace(r'亿', '')) * 100000000
                else:
                    item['total_recommend']=total_recommend
            except:
                item['total_recommend'] = 0
            item['lastupdate'] = response.xpath('//em[@class="time"]/text()').extract_first()
            item['site'] = 'qidian'
            item['type'] = 'novel'
            item['spiderid'] = 'qidian'
            item['current_date'] = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            item['category'] = ' '.join(response.xpath('//div[starts-with(@class,"crumbs-nav")]/span/a/text()').extract()[1:-1])
            item['status'] = response.xpath(
                '/html/body/div[2]/div[6]/div[1]/div[2]/p[1]/span[1]/text()').extract_first()
            item['description'] = response.xpath('//div[@class="book-intro"]/p/text()').extract_first()

            item['description'] = item['description'].strip().strip('\\r')
            item['biaoqian'] = ' '.join(response.xpath('//p[@class="tag"]/a/text()').extract())
            item['url'] = response.meta['bookurl']
            item['comment_count'] = response.xpath('//span[@id="J-discusCount"]/text()').extract_first()
            item['image'] = response.xpath('//div[@class="book-img"]/a/img/@src').extract_first()
            item['image'] = item['image'].strip().strip('\\r')
            item['banquan'] = ''
            item['hongbao'] = response.xpath('//div[@class="ticket"]/p/i/text()').extract_first()
            item['current_date'] = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            item['baoqian'] = ' '.join(response.xpath('//p[@class="tag"]/span/text()').extract())
            item['pubtime'] = ''
            item['points'] = 0
            item['yuepiaoorder']=0
            item['haopingzhishu'] = '0.0'
            item['shoucang'] = 0
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

            isVIP = response.xpath('//div[@class="book-info "]/p/span[3]/text()').extract_first()
            try:
                item['isvip'] = isVIP
            except:
                item['isvip'] = 'isnotVIP'


            authorId = re.search('data-authorid=\"(\d+)\"',response.text).group(1)
            bookId = re.search('(\d+)', response.meta['bookurl']).group(1)
            baseurl = 'https://book.qidian.com/ajax/book/GetBookForum?'
            parmas = {
                '_csrfToken': _csrfToken,
                # 'authorId': response.xpath('/html/body/div[2]/div[6]/div[1]/div[2]/h1/span/a/@href').re('\d+')[0],
                'authorId': authorId,
                'bookId': bookId,
                # 'chanId': response.xpath('/html/body/div[2]/div[4]/span/a[3]').re('chanId=(\d+)')[0],
                'chanId': re.search('g_data.chanId = (\d+)', response.text).group(1)
            }

            try:
                ####男生女生榜
                url = baseurl + urlencode(parmas)
                yield scrapy.Request(url, callback=self.parse_comment, meta={'item': item,'bookId':bookId})
            except:
                ####出版物

                url = 'https:' + response.xpath('//li[@class="j_discussion_block"]/a/@href').extract_first()
                yield scrapy.Request(url, meta={'item': item}, callback=self.parse_comment_publish)

    #
    def parse_comment_publish(self,response):
        item = response.meta['item']
        parmas_grade = {
            '_csrfToken': 'SNeUuww6EXo61zRDvRJKMKi4Fj5NbjS3uyCINFgW',
            'bookId': re.search('(\d+)', item['url']).group(1),

        }
        item['comment_count'] = re.search('全部 \((\d+)\)', response.text).group(1)
        grade_url = 'https://book.qidian.com/ajax/comment/index?' + urlencode(parmas_grade)
        yield scrapy.Request(grade_url, meta={'item': item}, callback=self.parse_grade)

    #
    def parse_comment(self, response):

        item = response.meta['item']

        parmas_grade = {
            '_csrfToken': 'SNeUuww6EXo61zRDvRJKMKi4Fj5NbjS3uyCINFgW',
            'bookId': response.meta['bookId'],

        }
        content = json.loads(response.text)

        item['comment_count'] = content['data']['threadCnt']
        grade_url = 'https://book.qidian.com/ajax/comment/index?' + urlencode(parmas_grade)
        yield scrapy.Request(grade_url, meta={'item': item}, callback=self.parse_grade)

    def parse_grade(self,response):
        item = response.meta['item']
        info = json.loads(response.text)
        item['grade'] = info['data']['rate']
        yield item



    def create_font(self, font_file):
        if not os.path.exists('./fonts'):
            os.mkdir('./fonts')

        file_list = os.listdir('./fonts')
        if font_file not in file_list:
            url = 'https://qidian.gtimg.com/qd_anti_spider/' + font_file
            new_file = self.get_font(url)
            with open('./fonts/' + font_file, 'wb') as f:
                f.write(new_file)

        return TTFont('./fonts/' + font_file)

    def get_font(self,url):
        response = requests.get(url)
        font = TTFont(BytesIO(response.content))
        cmap = font.getBestCmap()
        font.close()
        return cmap

    def get_encode(self,cmap, values):
        WORD_MAP = {'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5', 'six': '6',
                    'seven': '7',
                    'eight': '8', 'nine': '9', 'period': '.'}
        word_count = ''
        list = values.split(';')

        list.pop(-1)
        for value in list:
            value = value[2:]
            key = cmap[int(value)]
            word_count += WORD_MAP[key]
        return word_count