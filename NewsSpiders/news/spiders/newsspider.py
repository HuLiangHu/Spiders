# -*- coding: utf-8 -*-
import scrapy
#from scrapy_redis.spiders import RedisSpider
import json
import re
from datetime import datetime
from news.items import News
from scrapy.utils.project import get_project_settings
import pymssql
import uuid

APP = '41395'
SECRET = '8be8172cc9fd49248cfe44e8efd0fa2a'

class NewsStatsSpider(scrapy.Spider):
    name = "news"
    start_urls = []

    def __init__(self):
        super(NewsStatsSpider, self).__init__()
        self.start_urls = self.get_start_urls()

    def get_start_urls(self):
        settings = get_project_settings()
        conn = pymssql.connect(
            server=settings['MSSQL_HOST'],
            user=settings['MSSQL_USER'],
            password=settings['MSSQL_PASSWD'],
            database=settings['MSSQL_DBNAME']
        )
        cursor = conn.cursor()
        cursor.execute(
            'SELECT personid,CName FROM xz_export_person;'
        )
        rows = cursor.fetchall()
        start_urls = []
        for row in rows: 
            start_urls.append('http://jisunews.market.alicloudapi.com/news/search?keyword=%s&_pid=%s'%(row[1],str(row[0])))
            start_urls.append('http://route.showapi.com/109-35?title=%s&page=1&showapi_sign=%s&showapi_appid=%s&maxResult=100&_pid=%s'%(row[1],SECRET,APP,str(row[0])))
        return start_urls

    def parse(self, response):
        result = json.loads(response.body_as_unicode())
        if 'showapi_res_body' in result:
            personid = re.search('_pid=([\w\-\d]+)',response.url).group(1)
            for item in result['showapi_res_body']['pagebean']['contentlist']: 
                news = News()
                news['oid'] = str(uuid.uuid1())
                news['url'] = item['link']
                news['website'] = item['source']
                news['title'] = item['title']
                news['publish_at'] = item['pubDate']
                news['personid'] = personid
                yield news
        if 'result' in result:
            personid = re.search('_pid=([\w\-\d]+)',response.url).group(1)
            for item in result['result']['list']: 
                news = News()
                news['oid'] = str(uuid.uuid1())
                news['url'] = item['weburl']
                news['website'] = item['src']
                news['title'] = item['title']
                news['publish_at'] = item['time']
                news['personid'] = personid
                yield news