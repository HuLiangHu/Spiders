#!/usr/bin/env python
# -*- coding: utf8 -*-

import logging
import datetime
import re
import pymysql
from  redis import Redis
import time
import datetime
import pytz

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
START_URLS = 'search:start_urls'

MYSQL_SERVER = 'mysql.crotondata.cn'
MYSQL_USER = ''
MYSQL_PASSWORD = ''
MYSQL_DB = 'newmedia_db'
MYSQL_PORT = 3306


tz = pytz.FixedOffset(480)

class TVRank(object):
    def __init__(self):
        self.redis = Redis(host = REDIS_HOST,port=REDIS_PORT)
 
    def get_albums(self):
        albums = []
        try:
            conn = pymysql.connect(
                user = MYSQL_USER,
                passwd = MYSQL_PASSWORD,
                db = MYSQL_DB,
                host = MYSQL_SERVER,
                charset = "utf8",
                use_unicode = True
                )
            cursor = conn.cursor()
            cursor.execute(
                'call sp_getDailyKeyWord();'
                )
            rows = cursor.fetchall() 
            start_urls = []
            for row in rows:
                keyword = re.sub('[ \d]+$','',row[0])
                keyword = re.sub('\(.*\)','',keyword)
                keyword = re.sub('（.*）','',keyword)
                keyword = re.sub(u'第.*季','',keyword)
                albums.append(keyword) 
            return albums 
        except Exception,e:
            print(e)
        finally:
            conn.close()
            return albums

    def initStartURL(self):
        albums = self.get_albums()
        #todayDate = datetime.datetime(startDate.year, startDate.month, startDate.day,tzinfo=tz)
        datetime.timedelta(days=1)
        today = datetime.datetime.now()
        yesterday = today - datetime.timedelta(days=1)
        starttime = int(time.mktime(datetime.datetime(yesterday.year,yesterday.month,yesterday.day).timetuple()))
        endtime = int(time.mktime(datetime.datetime(today.year,today.month,today.day).timetuple()))
        for album in albums:
            self.redis.rpush(START_URLS,'https://c.api.weibo.com/2/search/statuses/limited.json?antispam=0&dup=0&q=%s&access_token=2.00ZLWYdC0KWpTW73ca4f3acb4k45rD&starttime=%s&endtime=%s&onlynum=1' % (album,starttime,endtime))
            

if __name__ == "__main__":
    tvrank = TVRank() 
    tvrank.initStartURL()