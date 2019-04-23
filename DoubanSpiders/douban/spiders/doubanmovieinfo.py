# -*- coding: utf-8 -*-
"""Douban Movie Info Spider"""
import scrapy
import random
import json
import re
from datetime import datetime
from douban.items import DoubanMovieInfo
from scrapy.utils.project import get_project_settings
import pymysql
copy_cookies='bid=ttiFWkh66Go; ll="108296"; _vwo_uuid_v2=DBC73793EC9FBA91F65AD58BF03264F82|9f6467bfa7fc7563e3263841c3943a6c; push_noty_num=0; push_doumail_num=0; __yadk_uid=UtBYdX623bbwZYZVc5meXzjE2an4rWfs; viewed="27182196"; gr_user_id=3313db1a-0b7c-454c-a345-e4bac90fdee3; __utmc=30149280; __utmc=223695111; ps=y; dbcl2="194338282:8x/3CKaZEOU"; ck=jIGH; __utmv=30149280.19433; __utmz=30149280.1554362703.15.4.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmz=223695111.1555299708.28.9.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1555309825%2C%22https%3A%2F%2Fwww.douban.com%2F%22%5D; _pk_ses.100001.4cf6=*; __utma=30149280.1397031086.1548991656.1555307864.1555309825.29; __utma=223695111.965954757.1548991656.1555307864.1555309827.30; __utmb=223695111.0.10.1555309827; __utmb=30149280.10.10.1555309825; ap_v=0,6.0; _pk_id.100001.4cf6=16d7e24ae5e1fc1b.1548991655.28.1555315939.1555307864.'
class transCookie:
    def __init__(self, cookie):
        self.cookie = cookie
    def stringToDict(self):
        '''
        将从浏览器上Copy来的cookie字符串转化为Scrapy能使用的Dict
        :return:
        '''
        itemDict = {}
        items = self.cookie.split(';')
        for item in items:
            key = item.split('=')[0].replace(' ', '')
            value = item.split('=')[1]
            itemDict[key] = value
        return itemDict
def cookiemain():
    trans = transCookie(copy_cookies)
    return trans.stringToDict()
cookies=cookiemain()

class DoubanMovieInfoSpider(scrapy.Spider):
    """豆瓣电影信息爬虫"""
    name = "doubanmovieinfo"
    start_urls = ['http://api.douban.com/v2/movie/subject/26630781']
    apikeys = ['088acf79cc38fde819a06e6d64aaf9b8',
               '01e1232b205f406405a36981611dc12c', '03405aad00de230c09c11007029a6924']
    
    def __init__(self):
        super(DoubanMovieInfoSpider,self).__init__()
        self.download_delay = 1
        self.start_urls = self.get_start_urls()
    def get_start_urls(self):
        start_urls = []
        settings = get_project_settings()
        conn = pymysql.connect(
                user = settings['MYSQL_USER'],
                passwd = settings['MYSQL_PASSWD'],
                db = settings['MYSQL_DBNAME'],
                host = settings['MYSQL_HOST'],
                charset = "utf8",
                use_unicode = True
                )
        cursor = conn.cursor()
        cursor.execute(
            'call sp_spider_getdoubanids();'
            )
        rows = cursor.fetchall() 
        start_urls = []
        for row in rows:  
            id = row[0]
            start_urls.append('http://api.douban.com/v2/movie/subject/%s'%
            (id))
        return start_urls
    '''
    def next_requests(self):
        """Returns a request to be scheduled or none."""
        use_set = self.settings.getbool('REDIS_START_URLS_AS_SET')
        fetch_one = self.server.spop if use_set else self.server.lpop
        # XXX: Do we need to use a timeout here?
        found = 0
        while found < 16:
            data = fetch_one(self.redis_key)
            if not data:
                # Queue empty.
                break
            req = self.make_request_from_data(data)
            if req:
                yield req
                found += 1
            else:
                self.logger.debug("Request not made from data: %r", data)

        if found:
            self.logger.debug("Read %s requests from '%s'", found, self.redis_key)
    '''
    def make_request_from_data(self, data):
        """ By default, data is an URL."""
        if '://' in data:
            return self.make_requests_from_url(data)
        else:
            url = 'https://api.douban.com/v2/movie/subject/%s?apikey=%s' % (
                data, random.choice(self.apikeys))
            return self.make_requests_from_url(url)

    def parse(self, response):
        if response.status !=200:
            url='https://movie.douban.com/subject/{}/'.format(re.search('subject/(\d+)',response.url).group(1))
            headers={
                'Cookie': copy_cookies,
                'Host': 'movie.douban.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
            }
            yield scrapy.Request(url,callback=self.parse_item,headers=headers,cookies=cookiemain())
        else:
            info = json.loads(response.body_as_unicode())
            #info['_sys_collection'] = 'douban_movieinfo'
            #info['_sys_upset_fields'] = ['rating', 'wish_count']
            info['createdtime'] = str(datetime.now())
            #return info
            #'''
            item = DoubanMovieInfo()
            item['id'] = info['id']
            item['rating'] = info['rating']['average']
            item['ratings_count'] = info['ratings_count']
            item['comments_count'] = info['comments_count']
            item['reviews_count'] = info['reviews_count']
            item['wish_count'] = info['wish_count']
            item['collect_count'] = info['collect_count']
            item['year'] = info['year']
            item['image'] = info['images']['large']
            item['genres'] = ','.join(info['genres'])
            item['countries'] = ','.join(info['countries'])
            item['casts'] = ' / '.join([c['name'] for c in info['casts']])
            item['episodes_count'] = info['episodes_count'] if 'episodes_count' in info else '-1'
            item['title'] = info['title']
            item['original_title'] = info['original_title']
            item['directors'] = ','.join([c['name'] for c in info['directors']])
            item['aka'] = ','.join(info['aka'])
            item['type'] = info['subtype']
            url = info['alt']
            yield scrapy.Request(url, meta={'item': item}, callback=self.parse_duration)

    def parse_duration(self, response):
        item = response.meta['item']
        try:
            duration = re.search('<span class="pl">片长|单集片长:</span> (.*)<br/>', response.text)
        except AttributeError:
            duration = re.search('片长:</span>.*?>(.*?)<', response.text)
        except:
            duration = None
        if duration:
            item['duration'] = duration.group(1)
        else:
            item['duration'] = None
        yield item
        #'''

    def parse_item(self,response):
        item = DoubanMovieInfo()
        item['id'] = re.search('(\d+)',response.url).group(1)
        info = json.loads(re.search('<script type="application/ld\+json">(.*?)</script>',response.text,re.S).group(1),strict=False)
        item['rating'] = response.xpath('//div[@class="rating_self clearfix"]/strong/text()').extract_first()
        item['ratings_count'] = response.xpath('//div[@class="rating_self clearfix"]//div[@class="rating_sum"]/a/span/text()').extract_first()
        try:
            item['comments_count'] = re.search('(\d+)',response.xpath('//div[@id="comments-section"]//h2/span/a/text()').extract_first()).group(1)
        except:
            item['comments_count'] =None
        try:
            item['reviews_count'] = re.search('(\d+)',response.xpath('//header/h2//a[@href="reviews"]/text()').extract_first()).group(1)
        except:
            item['reviews_count'] = None
        try:
            item['wish_count'] =  re.search('(\d+)人想看',response.text).group(1)
            item['collect_count'] = re.search('(\d+)人看过',response.text).group(1)
        except:
            item['wish_count'] = None
            item['collect_count'] = None
        item['year'] =info['datePublished']
        item['image'] = info['image']
        item['genres'] =','.join(info['genre'])
        try:
            item['countries'] =re.search('>制片国家/地区:</span> (.*?)<br/>',response.text).group(1)
        except:
            item['countries'] =None
        item['casts'] =','.join([i['name'] for i in info['actor']])[:500]
        try:
            item['episodes_count'] =re.search('>集数:</span> (.*?)<br/>',response.text).group(1)
        except:
            item['episodes_count'] =None
        item['title'] =response.xpath('//h1/span/text()').extract_first()
        try:
            item['original_title'] =response.xpath('//h1/span/text()').extract_first().split(' ')[1]
        except:
            item['original_title']=None
        item['directors'] =','.join([i['name'] for i in info['director']])
        try:
            item['aka'] = re.search('>又名:</span>(>*?)<br/>',response.text).group(1)
        except:
            item['aka']=None
        type = info['@type']
        if type=='Movie':
            item['type'] ='movie'
        else:
            item['type'] ='tv'
        try:
            duration = re.search('<span class="pl">片长|单集片长:</span> (.*)<br/>', response.text)
        except AttributeError:
            duration = re.search('片长:</span>.*?>(.*?)<', response.text)
        except:
            duration=None
        if duration:
            item['duration'] = duration.group(1)
        else:
            item['duration'] = None
        yield item