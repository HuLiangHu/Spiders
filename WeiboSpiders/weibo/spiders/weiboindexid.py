# -*- coding: utf-8 -*-
import scrapy
from datetime import date
import json
import time
import re
import pymysql
from datetime import datetime,timedelta
from weibo.items import WeiboIndexId
from scrapy.utils.project import get_project_settings
import urllib

class WeiboIndexIdSpider(scrapy.Spider):
    name = "weiboindexid"
    start_urls = (  )
    #custom_settings = {
        #"SCHEDULER" : "scrapy_redis.scheduler.Scheduler",
        #"SCHEDULER_QUEUE_CLASS" : "scrapy_redis.queue.SpiderPriorityQueue" 
    #}
    def __init__(self):
        super(WeiboIndexIdSpider,self).__init__()
        self.start_urls = self.get_start_urls()
    #
    def get_start_urls(self):
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
            'call sp_spider_get_weiboindexwords();'
            )
        rows = cursor.fetchall()
        return rows
    def start_requests(self):
        headers={
        'Host': 'data.weibo.com',
        'Origin': 'http://data.weibo.com',
        'Referer': 'http://data.weibo.com/index/newindex?visit_type=search',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Mobile Safari/537.36'
    }
        # with open('D:\workplace\oct16\spiders\WeiboSpiders\weibo\微指数.txt','r',encoding='utf-8') as f:
        #     names = f.readlines()
        for name in self.get_start_urls():
            data={
                'word':str(name[0]).strip()
            }
            yield scrapy.FormRequest('http://data.weibo.com/index/ajax/newindex/searchword',method='POST',formdata=data,headers=headers)
    def parse(self, response):
        #print(response.text)
        js_obj = json.loads(response.text)
        if js_obj['code'] == 100:
            wid = re.search('<li wid=\\\\\"(\d+)\\\\\"', response.body_as_unicode()).group(1)
            word = re.search('word=\\\\"(.*?)">', response.body_as_unicode()).group(1)
            word =word.rstrip('\\').encode("utf-8").decode("unicode_escape")
            item = WeiboIndexId()
            item['word'] = word
            item['wid'] = wid
            yield item