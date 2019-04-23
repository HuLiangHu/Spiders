# -*- coding: utf-8 -*-
import scrapy
import json
import re
from datetime import datetime
from weibo.items import WeiboStats
import pymysql
from scrapy.utils.project import get_project_settings

class WeiboStatsSpider(scrapy.Spider):
    name = "weibostats"
    start_urls = []
    
    def __init__(self):
        super(WeiboStatsSpider,self).__init__()
        self.start_urls = self.get_start_urls()
    
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
            'call sp_spider_getweiboids();'
            )
        rows = cursor.fetchall()
        num = 0
        tempArray = []
        start_urls = []
        for row in rows:
            tempArray.append(str(row[0]))
            if(num<=40):
                num = num + 1
                continue
            tempArray.append(str(row[0]))
            start_urls.append('https://api.weibo.com/2/users/counts.json?access_token=2.00ZLWYdC0KWpTW73ca4f3acb4k45rD&uids=%s' %','.join(tempArray))
            num = 0
            tempArray = []

        if len(tempArray)>0:
            start_urls.append('https://api.weibo.com/2/users/counts.json?access_token=2.00ZLWYdC0KWpTW73ca4f3acb4k45rD&uids=%s' %','.join(tempArray))
        return start_urls

    # def get_start_urls(self):
    #     import pandas as pd
    #     tempArray = []
    #     start_urls = []
    #     for id in pd.read_excel(r'D:\workplace\Oct25\spiders\作者微博贴吧名单截止20181023.xlsx')['weibo_id']:
    #
    #         if len(str(id))>4:
    #             tempArray.append(str(id))
    #             start_urls.append('https://api.weibo.com/2/users/counts.json?access_token=2.00ZLWYdC0KWpTW73ca4f3acb4k45rD&uids=%s' %','.join(tempArray))
    #             tempArray = []
    #
    #     if len(tempArray)>0:
    #         start_urls.append('https://api.weibo.com/2/users/counts.json?access_token=2.00ZLWYdC0KWpTW73ca4f3acb4k45rD&uids=%s' %','.join(tempArray))
    #     return start_urls


    def parse(self, response):
        js_obj = json.loads(response.body_as_unicode().replace("'", '"'))
        for item in js_obj:
            weibostats = WeiboStats()
            weibostats["weiboid"]=item['id']
            weibostats["followers_count"]=item['followers_count']
            weibostats["friends_count"]=item['friends_count']
            weibostats["statuses_count"]=item['statuses_count']
            weibostats["day"]=str(datetime.today())
            yield weibostats
            