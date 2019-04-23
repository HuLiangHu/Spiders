# -*- coding: utf-8 -*-
from urllib.parse import urlencode

import scrapy
#from scrapy_redis.spiders import RedisSpider
import json
import re
from datetime import datetime
from tieba.items import TiebaStats
from scrapy.utils.project import get_project_settings
import pymysql
import logging
# import pandas as pd
class TiebaStatsSpider(scrapy.Spider):
    name = "tiebastats"
    headers = {
        'referer': 'https://tieba.baidu.com/index.html',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }
    start_urls = []
    #
    def __init__(self):
        super(TiebaStatsSpider,self).__init__()
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
            'call sp_spider_gettiebaurls();'
            )
        rows = cursor.fetchall()
        start_urls = []
        for row in rows:
            url = row[0]
            if url.startswith('http://'):
                start_urls.append(url)
            else:
                logging.debug('"%s" is not a valid url' %url)
        return start_urls

    # def start_requests(self):
    #
    #     for keyword in pd.read_excel(r'D:\workplace\Oct25\spiders\漫画贴吧list.xls')['tieba_name']:
    #        # keyword ='艾小图'
    #         parmas ={
    #             'ie':'utf-8',
    #             'kw':keyword
    #         }
    #         url ='https://tieba.baidu.com/f?'+urlencode(parmas)
    #         yield scrapy.Request(url,meta={'keyword':keyword,'proxy':'http://103.43.40.104:47119','dont_redirect': True,'handle_httpstatus_list': [302]},headers=self.headers)
    #         self.headers['referer'] =url

    def parse(self, response):
        item = TiebaStats()
        thread_count = 0
        post_count = 0
        member_count = 0
        sign_count = 0
        #name = response.meta['keyword']

        name = re.search(u"forumName:.?'([^']+)',", response.body_as_unicode()).group(1)
        #print(name)


        if re.search(u'共有主题数<span class="red_text">(\d+)</span>',response.body_as_unicode()):
            thread_count = re.search(u'共有主题数<span class="red_text">(\d+)</span>',response.body_as_unicode()).group(1)
        elif re.search(u'"?thread_num"?: ?"?(\d+)"?',response.body_as_unicode()):
            thread_count = re.search(u'"?thread_num"?: ?"?(\d+)"?',response.body_as_unicode()).group(1)

        if re.search(u'贴子数.+<span class="red_text">(\d+)</span>篇',response.body_as_unicode(),re.S):
            post_count = re.search(u'贴子数.+<span class="red_text">(\d+)</span>篇',response.body_as_unicode(),re.S).group(1)

        elif re.search(u'"?post_num"?: ?"?(\d+)"?',response.body_as_unicode()):
            post_count = re.search(u'"?post_num"?: ?"?(\d+)"?',response.body_as_unicode()).group(1)

        elif re.search(u'"?post_num"?: ?"?(\d+)"?',response.body_as_unicode()):
            post_count = re.search(u'"?post_num"?: ?"?(\d+)"?',response.body_as_unicode()).group(1)
        if re.search(u"'memberNumber': ?'(\d+)',",response.body_as_unicode()):
            member_count = re.search(u"'memberNumber': ?'(\d+)',",response.body_as_unicode()).group(1)
        elif re.search(u'"memberNumber": ?"(\d+)",',response.body_as_unicode()):
            member_count = re.search(u'"memberNumber": ?"(\d+)",',response.body_as_unicode()).group(1)
        elif re.search(u'"?member_num"?: ?"?(\d+)"?',response.body_as_unicode()):
            member_count = re.search(u'"?member_num"?: ?"?(\d+)"?',response.body_as_unicode()).group(1)
        if re.search(u'"current_rank_info":{"sign_count":(\d+),',response.body_as_unicode()):
            sign_count = re.search(u'"current_rank_info":{"sign_count":(\d+),',response.body_as_unicode()).group(1)

        categorymatch = re.search(u'<span>目录：</span>[^<>]+<a[^>]+>([^<>]+)</a>',response.body_as_unicode(),re.M)#.group(1)
        if not categorymatch:
            categorymatch = re.search(u'stats-data="area=frs_dir"  target="_blank">([^<>]+)</a>',response.body_as_unicode(),re.M)
        if categorymatch:
            category = categorymatch.group(1)
        else:
            category = ''
        # for info in json.loads(infos):
        #     item['thread_count']
        item['url'] = response.url
        item['name'] = name
        item['category'] = category
        item['thread_count'] = thread_count
        item['post_count'] = post_count
        item['member_count'] = member_count
        item['sign_count'] = sign_count
        item['day'] = str(datetime.today())
        return item