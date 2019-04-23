# -*- coding: utf-8 -*-
import scrapy
from datetime import date
import json
import time
import re
import pymysql
from datetime import datetime,timedelta
from weibo.items import WeiboIndex
import urllib

class WeiboIndexIdSpider(scrapy.Spider):
    name = "weiboindex"
    #custom_settings = {
        #"SCHEDULER" : "scrapy_redis.scheduler.Scheduler",
        #"SCHEDULER_QUEUE_CLASS" : "scrapy_redis.queue.SpiderPriorityQueue"
    #}
    def get_start_urls(self):
        settings = self.settings
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
            "call sp_spider_getindexkeywords('weibo');"
            )
        rows = cursor.fetchall()
        return rows
    def start_requests(self):
        headers={
        'Host': 'data.weibo.com',
        'Origin': 'https://data.weibo.com',
        'Referer': 'https://data.weibo.com/index/newindex?visit_type=search',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Mobile Safari/537.36'
        }
         
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
            data = {
                'wid':str(wid),
                'dateGroup': '1month',
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
                'Referer': 'http://data.weibo.com/index/newindex?visit_type=trend&wid={}'.format(wid),
                'Host': 'data.weibo.com',
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': 'http://data.weibo.com'
            }
            yield scrapy.FormRequest('http://data.weibo.com/index/ajax/newindex/getchartdata',callback=self.parse_index, method='POST', formdata=data, headers=headers, meta={'wid': wid},
                                     dont_filter=True)

    def parse_index(self, response):
        res = json.loads(response.text)
        try:
            for i in res['data']:
                indexs = i['trend']['s'][::]
                days = i['trend']['x'][::]
                for index, day in zip(indexs, days):
                    weiboindex = WeiboIndex()
                    #weiboindex ={}
                    weiboindex['keyword'] =i['trend']['name']
                    weiboindex["wid"] = i['trend']['wid']
                    weiboindex["pc"] = None
                    weiboindex["mobile"] = None
                    weiboindex["total"] = index
                    cur_date = '%s年%s' % (datetime.now().year, day)
                    month = re.search('(\d+)月', cur_date).group(1)
                    # print(month)
                    M =time.strftime('%Y-%m', time.localtime(time.time()))
                    if int(month) >int(M.split('-')[1]):
                        cur_date = '%s年%s' % (datetime.now().year - 1, day)
                    else:
                        cur_date = '%s年%s' % (datetime.now().year, day)
                    mydate = time.strptime(cur_date, '%Y年%m月%d日')
                    weiboindex["day"] = time.strftime('%Y-%m-%d', mydate)

                yield weiboindex
        except:
            pass
