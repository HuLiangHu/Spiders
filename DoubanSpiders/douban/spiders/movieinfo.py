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



class MovieInfoSpider(scrapy.Spider):
    """豆瓣电影信息爬虫"""
    name = "movieinfo"
    start_urls = ['http://api.douban.com/v2/movie/subject/26630781']
    # apikeys = ['088acf79cc38fde819a06e6d64aaf9b8',
    #            '01e1232b205f406405a36981611dc12c', '03405aad00de230c09c11007029a6924']
    custom_settings ={
        'Host': 'movie.douban.com',
        'Referer': 'http://api.douban.com/v2/movie/subject/26630781',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }


    def __init__(self):
        super(MovieInfoSpider, self).__init__()
        self.download_delay = 2
        self.start_urls = self.get_start_urls()

    def get_start_urls(self):
        start_urls = []
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
            "SELECT id FROM `newmedia_db`.`tbl_doubantv` where type <> 'movie' AND `duration` IS NULL"
        )

        rows = cursor.fetchall()
        start_urls = []
        for row in rows:
            id = row[0]
            start_urls.append('http://api.douban.com/v2/movie/subject/{}'.format(id))
        return start_urls


    def parse(self, response):
        info = json.loads(response.body_as_unicode())
        # info['_sys_collection'] = 'douban_movieinfo'
        # info['_sys_upset_fields'] = ['rating', 'wish_count']
        info['createdtime'] = str(datetime.now())
        # return info
        # '''
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
        item['episodes_count'] = info['episodes_count'] if 'episodes_count' in info else '-1'
        item['title'] = info['title']
        item['original_title'] = info['original_title']
        item['directors'] = ','.join([c['name'] for c in info['directors']])
        item['aka'] = ','.join(info['aka'])
        item['type'] = info['subtype']
        url = info['alt']
        yield scrapy.Request(url,meta={'item': item}, callback=self.parse_duration)

    def parse_duration(self, response):
        item = response.meta['item']
        if '片长' in response.text:
            try:
                item['duration'] = re.search('<span class="pl">单集片长:</span> (.*)<br/>',response.text).group(1)

            except AttributeError as e:
                item['duration'] = re.search('<span class="pl">单集片长:</span> (.*).*?<br/>',response.text).group(1)
        else:
            item['duration'] = None
        yield item


