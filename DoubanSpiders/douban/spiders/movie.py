# -*- coding: utf-8 -*-
import scrapy
import json
import re
import random
from datetime import datetime
from scrapy.utils.project import get_project_settings
#import pymysql
import random
#from scrapy_redis import connection


class DoubanNewTVSpider(scrapy.Spider):
    name = "newtv2"
    
    start_urls = ['https://movie.douban.com/j/new_search_subjects?sort=U&range=1,10&tags=电视剧&start=0&countries=']
    
    apikeys = ['088acf79cc38fde819a06e6d64aaf9b8',
               '01e1232b205f406405a36981611dc12c', '03405aad00de230c09c11007029a6924']
    def start_requests(self):
        #self.server = connection.from_settings(self.settings)
        for item in ['美国','台湾','日本','韩国','英国','法国','德国','意大利','西班牙','印度','泰国','俄罗斯','伊朗','加拿大','澳大利亚','爱尔兰','瑞典','巴西','丹麦']:
            yield scrapy.Request('https://movie.douban.com/j/new_search_subjects?sort=U&range=1,10&tags=电视剧&start=0&countries=%s' %item)

    def parse(self, response):
        subjects = json.loads(response.body_as_unicode())
        for subject in subjects['data']:
            yield subject
        '''
            url = 'https://api.douban.com/v2/movie/subject/%s?apikey=%s' % (
                subject['id'], random.choice(self.apikeys))
            yield scrapy.Request(url,callback = self.parse_info)
        '''
        if len(subjects['data'])>0:
            start = int(re.search('start=(\d+)',response.url).group(1))
            start = start + 20
            url = re.sub('start=\d+','start=%s'%start,response.url)
            yield scrapy.Request(url)
            #self.server.lpush('doubanmovieinfo:start_urls', subject['id'])
        
    def parse_info(self,response):
        info = json.loads(response.body_as_unicode())
        info['createdtime'] = str(datetime.now())
        info['updatedtime'] = str(datetime.now())
        info['_sys_collection'] = 'douban_movieinfo'
        info['_sys_upset_fields'] = ['rating', 'wish_count','updatedtime']
        return info