# -*- coding: utf8 -*-
import scrapy
import json
import re
from scrapy.conf import settings
from weibo.items import WeiboItem
from dateutil import parser

class TimelineSpider(scrapy.Spider):
    name = "timeline"
    PAGE_COUNTCOUNT = 50 
    ACCESS_TOKEN = settings.get('WEIBO_TOKEN', '2.00ZLWYdC0KWpTW73ca4f3acb4k45rD')
    URL_TEMPLATE = 'https://c.api.weibo.com/2/statuses/user_timeline_batch.json?uids=%s&count=50&page=1&access_token=%s'
    #URL_TEMPLATE = 'https://c.api.weibo.com/2/search/statuses/limited.json?ids=%s&count=50&page=1&access_token=%s'
    start_urls = [
        'https://weibo.com/sitannisilafusiji'
    ]

    def __init__(self, *args, **kwargs):
        super(TimelineSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        #self._increment_status_code_stat(response)
        requrl = response.request.url
        redirect_urls = response.request.meta['redirect_urls']
        ori_url = None
        if len(redirect_urls)>0:
            ori_url = redirect_urls[0]
        if re.search('((http|https):\/\/)weibo\.com\/u\/\d+', requrl):
            uid = re.search('weibo\.com\/u\/(\d+)', requrl).group(1)
            #https://c.api.weibo.com/2/users/show_batch/other.json
            url = self.URL_TEMPLATE % (uid,self.ACCESS_TOKEN)
            req = scrapy.Request(url, meta=response.meta, callback = self.parse)
            req.meta['profile_url'] = requrl
            yield req 

        elif re.search('((http|https):\/\/)weibo\.com\/\w+', requrl):
            domain = re.search('weibo\.com\/(\w+)', requrl).group(1)
            #https://api.weibo.com/2/users/domain_show.json
            req = scrapy.Request('https://api.weibo.com/2/users/domain_show.json?access_token=%s&domain=%s'%(self.ACCESS_TOKEN,domain), meta=response.meta, callback = self.parse)
            req.meta['profile_url'] = requrl
            yield req

        elif re.search('^(http|https)\:\/\/api\.weibo\.com\/2\/users', requrl):
            jsonObj = json.loads(response.body)  
            yield scrapy.Request(self.URL_TEMPLATE % (jsonObj['id'],self.ACCESS_TOKEN), meta=response.meta, callback=self.parse)

        elif re.search('((http|https):\/\/)c\.api\.weibo\.com\/2\/statuses', requrl):
            try:
                timeline = json.loads(response.body)
            except:
                timeline = json.loads(response.text)
            if 'error_code' in timeline: 
                if str(timeline['error_code']) == '21405':
                    yield scrapy.Request(url = response.url, meta=response.meta, callback = self.parse) 
            else:
                if re.search('page=1&',requrl):
                        max_page = int(timeline['total_number'] / 50)
                        if max_page > 20:
                            max_page = 20
                        for i in range(2,max_page + 1):
                            next_url = re.sub('page=1','page=%d' %i,requrl)
                            yield scrapy.Request(next_url, meta=response.meta, callback=self.parse)
                for status in timeline['statuses']:
                    weiboitem = WeiboItem()
                    for field in weiboitem.fields:
                        try:
                            if field in status.keys():
                                weiboitem[field] = status[field]
                        except Exception as e:
                            print(e)
                    weiboitem['user_id'] = status['user']['id']
                    weiboitem['profile_url'] = response.meta['profile_url']
                    createdtime = parser.parse(status['created_at']) 
                    weiboitem['created_at'] = createdtime
                    weiboitem['url'] = response.request.url
                    re_emoji = re.compile(u'[^\u0000-\uD7FF\uE000-\uFFFF]')
                    # re_emoji = re.compile(u'('u'\ud83c[\udf00-\udfff]|'u'\ud83d[\udc00-\ude4f\ude80-\udeff]|'u'[\u2600-\u26FF\u2700-\u27BF])+',re.UNICODE)
                    weiboitem['text'] = re_emoji.sub(' ',weiboitem['text'])
                    weiboitem['source'] = re_emoji.sub(' ',weiboitem['source'])
                    yield weiboitem
        
        elif ori_url and re.search('((http|https):\/\/)weibo\.com\/u\/\d+',ori_url):
            uid = re.search('weibo\.com\/u\/(\d+)', ori_url).group(1)
            #https://c.api.weibo.com/2/users/show_batch/other.json
            url = self.URL_TEMPLATE % (uid,self.ACCESS_TOKEN)
            req = scrapy.Request(url, meta=response.meta, callback = self.parse)
            req.meta['profile_url'] = ori_url
            yield req
        elif  ori_url and re.search('((http|https):\/\/)weibo\.com\/\w+', ori_url):
            domain = re.search('weibo\.com\/(\w+)', ori_url).group(1)
            #https://api.weibo.com/2/users/domain_show.json
            req = scrapy.Request('https://api.weibo.com/2/users/domain_show.json?access_token=%s&domain=%s'%(self.ACCESS_TOKEN,domain), meta=response.meta, callback = self.parse)
            req.meta['profile_url'] = ori_url
            yield req
        
        else:
            print(ori_url)
            print(requrl)
            print('*'*100)
            pass