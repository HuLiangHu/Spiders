# -*- coding: utf-8 -*-
import scrapy
import json
import re
import pymysql
import redis
from datetime import date, datetime, timedelta
from wechat.items import WeChatIndex
from scrapy.utils.project import get_project_settings
import time
import logging


class WeChatIndexSpider(scrapy.Spider):
    name = "wechatindex"
    template_url = 'https://search.weixin.qq.com/cgi-bin/searchweb/wxindex/querywxindexgroup?group_query_list=%s&wxindex_query_list=%s&gid=&openid=%s&search_key=%s'
    start_key = 'wechat:index:keywords'
    token_key = 'wechat:index:token'
    custom_settings = {
        "DOWNLOAD_DELAY":3,
        "DEFAULT_REQUEST_HEADERS": {
            'Accept': '*/*',
            'Accept-Language': 'zh-cn',
            'Accept-Encoding': 'br, gzip, deflate',
            'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 11_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15G77 MicroMessenger/6.7.0 NetType/WIFI Language/zh_CN',
            'Refere': 'https://servicewechat.com/wxc026e7662ec26a3a/4/page-frame.html',
        }
    }
    start_urls = []

    def __init__(self):
        super(WeChatIndexSpider, self).__init__()
        self.init_tasks()

    def init_tasks(self):
        settings = get_project_settings()
        self.server = redis.Redis(host=settings['REDIS_HOST'], port=settings['REDIS_PORT'],password=settings['REDIS_PASSWORD'])
        
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
            'call sp_spider_getwechatindexkeyword();'
        )
        self.server.delete(self.start_key)
        rows = cursor.fetchall()
        for row in rows:
            value = row[0]
            value = row[0].replace(';', '')
            self.server.rpush(self.start_key, value)
        
    def next_request(self):
        """Returns a request to be scheduled or none."""
        openid, search_key = self._getToken()
        keywords = ';'.join([key.decode('utf8') for key in  self.server.lrange(self.start_key, 0, 3)])
        url = self.template_url % (keywords, keywords, openid, search_key)
        logging.debug(url)
        return scrapy.Request(url=url,dont_filter=True)

    def start_requests(self):
        openid, search_key = self._getToken()
        keywords = ';'.join([key.decode('utf8') for key in  self.server.lrange(self.start_key, 0, 3)])
        url = self.template_url % (keywords, keywords, openid, search_key)
        return [scrapy.Request(url=url)]

    def parse(self, response):
        js_obj = json.loads(response.body_as_unicode().replace("'", '"'))
        if js_obj['errcode'] == 0:
            self.server.ltrim(self.start_key, 4, -1)
            for item in js_obj['data']['group_wxindex']:
                latestDay = datetime.today() - timedelta(days=1)
                i = 0
                for value in item['wxindex_str'].split(','):
                    wechatindex = WeChatIndex()
                    wechatindex["keyword"] = item['query']
                    if value == '':
                        value = 0
                    wechatindex["total"] = value
                    wechatindex["day"] = latestDay - timedelta(days=i)
                    i = i + 1
                    yield wechatindex

            openid, search_key = self._getToken()
            keywords = ';'.join([key.decode('utf8') for key in  self.server.lrange(self.start_key, 0, 3)])
            url = self.template_url % (keywords, keywords, openid, search_key)
            logging.debug(url)
            yield scrapy.Request(url=url)
        else:
            self.server.delete(self.token_key)
            while True:
                openid, search_key = self._getToken()
                if openid:
                    url = re.sub('openid=[^&]+', 'openid=%s' % openid, response.url)
                    url = re.sub(
                        'search_key=[^&]+', 'search_key=%s' % search_key, url)
                    yield scrapy.Request(url=url,dont_filter=True)
                    break
                else:
                    logging.info('Sleep 5 sec...')
                    time.sleep(5)

    def _getToken(self):
        token = self.server.get(self.token_key)
        if token:
            openid = token.decode('utf8').split(' ')[0]
            search_key = token.decode('utf8').split(' ')[1]
            return openid, search_key
        return None, None
