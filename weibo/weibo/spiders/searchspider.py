#!/usr/bin/env python
# -*- coding: utf8 -*-

from datetime import datetime, timedelta
import logging
from scrapy.conf import settings
from scrapy.exceptions import CloseSpider
from scrapy.http import Request
from scrapy.spiders import Spider
from weibo.items import WeiboItem,UserItem
from scrapy.utils.project import get_project_settings
import re, json
from time import mktime
from urllib.parse import unquote 
from dateutil import parser
import pymysql
import datetime as dt


class SearchSpider(Spider):
    name = 'search'
    allowed_domains = ['weibo.com']   
    PAGE_COUNT = 50
    today = dt.date.today()
    month = today.month
    day = today.day
    def __init__(self):
        super(SearchSpider,self).__init__()
        self.start_urls = self.get_start_urls()
    
    def get_start_urls(self):
        settings = get_project_settings()
        keywords = ['南歌','锦绣南歌','雀谋','锦绣 2','锦绣长歌','南歌嘹亮']
        start_urls = []
        for keyword in keywords:
            # start_time = int(mktime(datetime(2019, self.month, self.day - 1).timetuple()))
            # end_time = int(mktime(datetime(2019, self.month, self.day).timetuple()))
            start_time = int(mktime(datetime(2018, 5,9).timetuple()))
            end_time = int(mktime(datetime(2018 ,6,27).timetuple()))
            start_urls.append('https://c.api.weibo.com/2/search/statuses/limited.json?antispam=1&dup=1&q=%s&access_token=2.00ZLWYdC0KWpTWd6c53a1181lvZOiB&starttime=%s&endtime=%s&onlynum=1'%(keyword,start_time,end_time))
            
        return start_urls  
    def start_requests(self):
        for url in self.start_urls:
            yield self.make_requests_from_url(url)

    def parse(self,response):
        try:
            results = json.loads(response.body_as_unicode())
            keyword = re.search('q=([^&]+)',response.url).group(1)
            keyword = unquote(keyword)
        except Exception as e:
            yield Request(url=response.url,callback=self.parse)
            return
        onlynum = re.search('onlynum=(\d)',response.url).group(1) == "1"
        if onlynum :
            if int(results['total_number']) > 1000:
                if int(results['total_number']) > 1000000  and not re.search('hasori=1',response.url):
                    if not re.search('hasori=1',response.url):
                        if re.search('hasori=0',response.url):
                            url = re.sub("hasori=0", "hasori=1",response.url)
                        else:
                            url = response.url + "&hasori=1"
                        yield Request(url,callback=self.parse,dont_filter=True)
                    else:
                        return
                else:
                    starttime =  int(re.search('starttime=(\d+)',response.url).group(1)) 
                    endtime = int(re.search('endtime=(\d+)',response.url).group(1))
                    mid = int((starttime+endtime)/2)

                    firstpart = response.url
                    secondpart = response.url
                    #first part 

                    firstpart = re.sub("endtime=\d+", "endtime=%d"%mid,firstpart)
                    yield Request(url = firstpart,callback=self.parse)

                    #second part
                    secondpart = re.sub("starttime=\d+", "starttime=%d"%mid,secondpart)
                    yield Request(url = secondpart,callback=self.parse,dont_filter=True)
            elif int(results['total_number'])>0:  
                url = re.sub("onlynum=\d", "onlynum=0",response.url)
                if not re.search('count=\d',url):
                    url +=  "&count=%d" %self.PAGE_COUNT
                if not re.search('page=\d',url):
                    url +=  "&page=1" 
                
                total_num = int(results['total_number'])
                if total_num>self.PAGE_COUNT:
                    if total_num %self.PAGE_COUNT ==0:
                        totalpage = int(total_num/self.PAGE_COUNT)
                    else:
                        totalpage = int(total_num/self.PAGE_COUNT) +1
                    for i in range(1,totalpage):
                        url = re.sub('page=\d+','page=%d'%i,url)
                        yield Request(url = url,callback = self.parse)
                else:
                    yield Request(url = url,callback=self.parse) 
        else:
            if 'statuses' in  results:
                for status in results['statuses']:
                    weiboitem,useritem = self.parse_status(status)
                    weiboitem['task_keys'] = [keyword]
                    access_token = re.search('access_token=([^&]+)',response.url).group(1) 
                    #source = re.search('source=(\d+)',response.url).group(1)
                    #url = 'https://api.weibo.com/2/tags.json?uid=%s&access_token=%s'%(useritem['id'],access_token) 
                    #url = 'https://c.api.weibo.com/2/tags/tags_batch/other.json?uids=%s&access_token=%s'%(useritem['id'],access_token)
                    #yield Request(url = url,callback = self.parse_usertags,meta={"user":useritem}) 
                    yield weiboitem
            else:
                if 'error_code' in results: 
                    if str(results['error_code']) == '21405':
                        yield Request(url = response.url,callback = self.parse) 
                    logging.log(logging.ERROR,"Error_Code:%s,Message:%s" % (results['error_code'],results['error']))  
    def parse_usertags(self,response):
        results = json.loads(response.body_as_unicode())
        user = response.meta['user'] 
        tags = []
        if len(results)>0:
            for item in results[0]['tags']:
                for attr in item:
                    if attr == 'flag' or attr=="weight":
                        continue
                    tags.append(item[attr]) 
        user['tags'] = tags
        yield user

    def parse_status(self,status):
        weiboitem = WeiboItem()
        for field in weiboitem.fields:
            try:
                if field in status.keys():
                    weiboitem[field] = status[field]  
            except Exception as e:
                print(e)
        weiboitem['user_id'] = status['user']['id']
        try:
            weiboitem['user_name'] = status['user']['name']
        except:
            try:
                weiboitem['user_name'] = status['user']['screen_name']
            except:
                weiboitem['user_name'] = ''
        createdtime = parser.parse(status['created_at']) 
        weiboitem['created_at'] = createdtime

        #weiboitem['created_at_obj'] = {'year':createdtime.year,'month':createdtime.month, 'day':createdtime.day, 'hour':createdtime.hour,'minute':createdtime.minute}

        useritem = UserItem()
        for field in useritem.fields:
            try:
                if field in status['user'].keys():
                    useritem[field] = status['user'][field]
            except Exception as e:
                print(e)
        weiboitem['clear_text'] = self.clear_weibo(weiboitem['text'])
        '''
        words = pseg.cut(weiboitem['clear_text'])
        s = SnowNLP(weiboitem['clear_text'])
        denoised = []
        # 去除数量词和无意义词
        for word in words:
            if word.flag not in ('x', 'm'):
                denoised.append(word.word)
        sen = s.sentiments
        weiboitem['sentiments'] = sen
        weiboitem['sentiments_text'] = -1 if sen <0.4 else 1 if sen>0.6 else 0;
        #for word in words:
        #    if word.flag not in ('x', 'm'):
        #        denoised.append(word.word)
         
        weiboitem['words_list'] = denoised
        '''
        return weiboitem,useritem 


    def clear_weibo(self,raw_content):
        content = re.sub(r'http:\/\/t\.cn\/[A-Za-z0-9]*','',raw_content)
        content = re.sub(r'\/\/@.+','',content)
        content = re.sub(r'@[^\s:]+','',content)
        return content
