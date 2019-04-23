# -*- coding: utf-8 -*-
import time
from datetime import datetime

import re
import scrapy
import http.cookiejar,urllib.request
import ssl
import json
from scrapy import Selector
from lxml import etree
import requests
import json
import pandas as pd
from urllib.parse import urlencode
from bs4 import BeautifulSoup
ssl._create_default_https_context = ssl._create_unverified_context
import pandas as pd

from .WeiboCookie import copy_cookie


class transCookie:
    def __init__(self, cookie):
        self.cookie = cookie
    def stringToDict(self):
        '''
        将从浏览器上Copy来的cookie字符串转化为Scrapy能使用的Dict
        :return:
        '''
        itemDict = {}
        items = self.cookie.split(';')

        for item in items:
            key = item.split('=')[0].replace(' ', '')
            value = item.split('=')[1]
            itemDict[key] = value
        return itemDict
def cookiemain():
    trans = transCookie(copy_cookie)
    return trans.stringToDict()

#print(cookiemain())
class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    #allowed_domains = ['weibo.com']
    baseurl = 'https://weibo.com/p/aj/v6/mblog/mbloglist?'
    api ='https://m.weibo.cn/api/container/getIndex?'
    containId ='https://m.weibo.cn/api/container/getIndex?type=uid&value={}'
    headers = {
        #'Host': 'weibo.com',
        'Cookie':copy_cookie,
        #'Referer': 'https://weibo.com/u/5264246287/home?wvr=5',
        # 'Upgrade-Insecure-Requests': '1',
        #'Cookie': 'UM_distinctid=16477effaebfa-0c3cb008317d4d-163e6952-13c680-16477effaec898; SINAGLOBAL=8411638962179.644.1531020573554; YF-Page-G0=7b9ec0e98d1ec5668c6906382e96b5db; _s_tentry=passport.weibo.com; Apache=3277359469844.7583.1531665352461; ULV=1531665352484:2:2:1:3277359469844.7583.1531665352461:1531020573560; YF-V5-G0=731b77772529a1f49eac82a9d2c2957f; TC-V5-G0=28bf4f11899208be3dc10225cf7ad3c6; TC-Page-G0=42b289d444da48cb9b2b9033b1f878d9; TC-Ugrow-G0=968b70b7bcdc28ac97c8130dd353b55e; login_sid_t=2f8da912b083dcb04b5efdfdaa6a3dd4; cross_origin_proto=SSL; WBtopGlobal_register_version=ad4825dfad48feef; YF-Ugrow-G0=5b31332af1361e117ff29bb32e4d8439; SCF=ArdNK7JAeiwZsfqijbHFsNSmOYKlz-07UoTqh9iHi1d5C9Xu16eMVH7qVf5p0JFdaq3ea-U2swGlF72-PjrJ-W4.; SUHB=05iKpokzA799hg; appkey=; ALF=1542785896; SUB=_2A252yQ44DeRhGeNM7VYT9CjOwzuIHXVSNZJwrDV8PUJbkNAKLVnMkW1NThMvEj479_iWcrCP7T8n4u99Ju9aOyD3; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WW889d9IOyFr2X9x2dfgFS.5JpX5oz75NHD95QfeoqXeoBceonNWs4Dqc_zi--fiKL8iKn0i--fiKLhi-i8i--ci-zRi-20i--ci-zfi-8Wi--Xi-i2i-27i--fi-2Xi-2Ni--NiKnRi-zNi--NiKLWiKnX; wvr=6; wb_view_log_5264246287=1440*9002; UOR=,,www.baidu.com; wb_timefeed_5264246287=1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }
    # def getTotalPage(self,url):
    #     response = requests.get(url,headers=self.headers)
    #     totalpage = response.json()['data']['cardlistInfo']['total']
    #     totalpage =int(totalpage)/10
    #     return totalpage



    def start_requests(self):

        with open('D:\workplace\oct16\spiders\PublicSentimentSpider\PublicSentimentSpider\spiders\weibo.txt','r',encoding='utf-8') as f:
            urls = f.readlines()
            for url in urls:
                if url:
                    print(url)
        #for url in pd.read_excel(r'D:\hulian\Documents\WXWork\1688851171353450\Cache\File\2019-02\青春有你W3.xlsx')['微博地址']:
        #for url in start_urls:
                    yield scrapy.Request(url,callback=self.parse_uid,cookies=cookiemain(),dont_filter=True)
    def parse_uid(self, response):
        uid = re.search('CONFIG\[\'oid\'\]=\'(.*)\'',response.text).group(1)
            #id ='1259110474'
        if len(str(uid))>4:
            url = self.containId.format(uid)
            yield scrapy.Request(url,meta={'id':uid},callback=self.parse_containerId,cookies=cookiemain())


    def parse_containerId(self, response):
       # print(response.text)
        content = json.loads(response.text)['data']
        for data in content['tabsInfo']['tabs']:
            if (data.get('tab_type') == 'weibo'):
                containerid = data.get('containerid')

        parmas ={
            'uid': response.meta['id'],
            'luicode': '10000011',
            'type': 'uid',
            'value': response.meta['id'],
            'containerid': containerid,
            'page': '1'
        }
        url = self.api+urlencode(parmas)
        yield scrapy.Request(url, callback=self.parse_item,meta={'parmas':parmas}, headers=self.headers, dont_filter=True,cookies=cookiemain())

    def parse_item(self, response):
        totalpage = json.loads(response.text)['data']['cardlistInfo']['total']
        totalpage = int(totalpage) / 10
        if json.loads(response.text)['data']['cards']:
            for info in json.loads(response.text)['data']['cards']:
                item ={}

                #if info['card_type'] =='9':
                try:
                    try:
                        item['weiboname'] = info['mblog']['user']['screen_name']
                    except:
                        pass
                    item['attitudes_count'] = info['mblog']['attitudes_count']
                    item['comments_count'] = info['mblog']['comments_count']
                    item['reposts_count'] = info['mblog']['reposts_count']
                    item['created_at'] = info['mblog']['created_at']
                    item['url'] = info['scheme']
                    content = info['mblog']['text']
                    item['content'] = re.sub('<.*?>', ' ', content)
                    item['crawldate'] = str(datetime.now()).split('.')[0]

                    yield item
                except:
                    pass

            parmas = response.meta['parmas']
            for page in range(1,5):
                parmas['page'] =page
                url = self.api+urlencode(parmas)
                yield scrapy.Request(url,callback=self.parse_item,meta={'parmas':parmas},headers=self.headers,cookies=cookiemain())
                self.headers['Referer'] =url

