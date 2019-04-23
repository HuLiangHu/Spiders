# -*- coding: utf-8 -*-
import scrapy
import json
import re
import random
from datetime import datetime
from scrapy.utils.project import get_project_settings
#import pymysql
import random
from douban.items import DoubanMovieInfo
#from scrapy_redis import connection


class DoubanMoviesSpider(scrapy.Spider):
    name = "movies"
    start_urls = ['https://movie.douban.com/j/new_search_subjects?sort=T&range=0,10&tags=电影,香港&start=0',
                  'https://movie.douban.com/j/new_search_subjects?sort=T&range=0,10&tags=电影,大陆&start=0']
    
    apikeys = ['088acf79cc38fde819a06e6d64aaf9b8',
               '01e1232b205f406405a36981611dc12c', '03405aad00de230c09c11007029a6924']
    def start_requests(self):
        #self.server = connection.from_settings(self.settings)
         
        for url in self.start_urls:
            yield scrapy.Request(url)

    def parse(self, response):
        subjects = json.loads(response.body_as_unicode())
        if len(subjects['data'])>0:
            start = int(re.search('start=(\d+)',response.url).group(1))
            nextPage = re.sub('start=\d+','start=%s' %(start+20),response.url)
            yield scrapy.Request(nextPage)
        for subject in subjects['data']: 
            url = 'https://api.douban.com/v2/movie/subject/%s?apikey=%s' % (
                subject['id'], random.choice(self.apikeys))
            yield scrapy.Request(url,callback = self.parse_info)
            #self.server.lpush('doubanmovieinfo:start_urls', subject['id'])
    def parse_info(self, response):
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
        item['casts'] = ','.join([c['name'] for c in info['casts']])
        item['episodes_count'] = info['episodes_count'] if 'episodes_count' in info and isinstance(info['episodes_count'],int) else '-1'
        item['title'] = info['title']
        item['original_title'] = info['original_title']
        item['directors'] = ','.join([c['name'] for c in info['directors']])
        item['aka'] = ','.join(info['aka'])
        item['type'] = info['subtype']
        return item