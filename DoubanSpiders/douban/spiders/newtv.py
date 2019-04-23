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
    name = "newtv"
    start_urls = ['https://movie.douban.com/j/search_subjects?type=tv&tag=%E5%9B%BD%E4%BA%A7%E5%89%A7&sort=time&page_limit=40&page_start=0',
                  'https://movie.douban.com/j/search_subjects?type=tv&tag=%E7%BB%BC%E8%89%BA&sort=time&page_limit=40&page_start=0', 
                  'https://movie.douban.com/j/search_subjects?type=tv&tag=%E6%B8%AF%E5%89%A7&sort=time&page_limit=20&page_start=0']
    
    apikeys = ['088acf79cc38fde819a06e6d64aaf9b8',
               '01e1232b205f406405a36981611dc12c', '03405aad00de230c09c11007029a6924']
    def start_requests(self):
        #self.server = connection.from_settings(self.settings)
        for url in self.start_urls:
            yield scrapy.Request(url)

    def parse(self, response):
        subjects = json.loads(response.body_as_unicode())
        for subject in subjects['subjects']:
            url = 'https://api.douban.com/v2/movie/subject/%s?apikey=%s' % (
                subject['id'], random.choice(self.apikeys))
            yield scrapy.Request(url,callback = self.parse_info)
            #self.server.lpush('doubanmovieinfo:start_urls', subject['id'])
    def parse_info(self,response):
        info = json.loads(response.body_as_unicode())
        info['createdtime'] = str(datetime.now())
        info['updatedtime'] = str(datetime.now())
        info['_sys_collection'] = 'douban_movieinfo'
        info['_sys_upset_fields'] = ['rating', 'wish_count','updatedtime']
        return info