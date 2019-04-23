#!/usr/bin/env python
# -*- coding: utf8 -*-
import scrapy
import logging
import re
import json
import random
from weibo.util import parse_weiboitems


class TimelineSpider(scrapy.Spider):
    name = 'timeline'
    allowed_domains = ['weibo.com', 'sina.com.cn', 'weibo.cn']
    APPIDS = ['878922546', '482040646', '1547618289',
              '166678827', '3052734250', '648004702']
    PAGE_COUNT = 50
    #URL_TEMPLATE = 'https://api.weibo.com/2/statuses/timeline_batch.json?source=479952302&uids=%s&count=200&page=1&access_token=2.00ZLWYdC0KWpTWa2a5ee4143rBMaoD&t=' + str(time.time())
    URL_TEMPLATE = 'http://api.sina.com.cn/weibo/2/statuses/timeline_batch.json?source=%s&uids=%s'
    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "ITEM_PIPELINES" : { 
            'weibo.pipelines.KafkaPipeline': 300
        }
    }

    def __init__(self, name=None, **kwargs):
        super(TimelineSpider, self).__init__(name, **kwargs)
        f = open('/weibo/userids.txt', 'r')  # 以读方式打开文件
        logging.debug("Loaded userids from file.")
        self.start_urls = []
        num = 0
        tempArray = []
        for line in f.readlines():
            num = num + 1
            line = line.strip()  # 去掉每行头尾空白
            if not len(line):  # 判断是否是空行或注释行
                continue  # 是的话，跳过不处理
            if(num <= 20):
                tempArray.append(line)
                continue
            self.start_urls.append(self.URL_TEMPLATE % (
                random.choice(self.APPIDS), ','.join(tempArray)))
            num = 0
            tempArray = []
        if len(tempArray) > 0:
            self.start_urls.append(self.URL_TEMPLATE % (
                random.choice(self.APPIDS), ','.join(tempArray)))

    def parse_user(self, response):
        jsonObj = json.loads(response.body_as_unicode())
        yield scrapy.Request(self.URL_TEMPLATE % jsonObj['id'])

    def parse(self, response):
        timeline = json.loads(response.body_as_unicode())
        if 'error_code' in timeline:
            if str(timeline['error_code']) == '21405':
                url = re.sub('source=\d+', 'source=%s' %
                             random.choice(self.APPIDS), response.url)
                yield scrapy.Request(url, callback=self.parse)
            logging.log(logging.ERROR, "Error_Code:%s,Message:%s" %
                        (timeline['error_code'], timeline['error']))
        else:
            result = timeline['result']
            for status in result['data']['statuses']:
                weiboitem,useritem = parse_weiboitems(status)
                yield weiboitem
                yield useritem
                #yield status
