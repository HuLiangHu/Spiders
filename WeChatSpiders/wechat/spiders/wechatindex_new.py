# -*- coding: utf-8 -*-
from urllib.parse import urlencode

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


class WeChatIndexNewSpider(scrapy.Spider):
    name = "wechatindex_new"
    start_api = 'http://zhishu.sogou.com/getDateData?'
    startDate = 20180406
    endDate =20190406
    def start_requests(self):
        with open('wechat.txt','r',encoding='utf-8') as f:
            keywords = f.readlines()
        for keyword in keywords:
            parmas ={
                'kwdNamesStr': keyword.strip(),
                'startDate': self.startDate,
                'endDate': self.endDate,
                'dataType': 'MEDIA_WECHAT',
                'queryType': 'INPUT'
            }
            url = self.start_api+urlencode(parmas)
            headers={
                #'Referer': 'http://zhishu.sogou.com/index/media/wechat?kwdNamesStr=%E5%8F%A4%E5%A4%A9%E4%B9%90&timePeriodType=YEAR&dataType=MEDIA_WECHAT&queryType=INPUT',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
            }
            yield scrapy.Request(url,meta={'name':keyword.strip()},headers=headers)

    def parse(self, response):

        for j in json.loads(response.text)['data']['pvList']:
            for i in j:
                #print(i)
                try:
                    item ={}
                    item['name'] = response.meta['name']
                    item['wechatid'] = i['id']
                    item['wechatindex'] = i['readTimes']
                    item['date'] = i['date']
                    yield item
                except:
                    pass