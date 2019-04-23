# -*- coding: utf-8 -*-
import scrapy
#from scrapy_redis.spiders import RedisSpider
import json
import re
from datetime import datetime
from tieba.items import TiebaStats
from scrapy.utils.project import get_project_settings
import pymysql
import logging

class TiebaSpider(scrapy.Spider):
    name = "tieba"
    start_urls = [
            'http://tieba.baidu.com/f/fdir?fd=%E7%94%B5%E8%A7%86%E5%89%A7&ie=utf-8&sd=%E5%86%85%E5%9C%B0%E7%94%B5%E8%A7%86%E5%89%A7',
            'http://tieba.baidu.com/f/fdir?fd=%E7%94%B5%E5%BD%B1&ie=utf-8&sd=%E5%86%85%E5%9C%B0%E7%94%B5%E5%BD%B1'
        ]
    
    def __init__(self):
        super(TiebaSpider,self).__init__()
    def parse(self,response):
        #items
        url_list = response.xpath('//div[@class="sub_dir_box"]/table/tr/td/a/@href').extract()
        for url in url_list:
            url = response.urljoin(url)
            yield scrapy.Request(url,callback = self.parse_item)
        #paging
        page_list = response.xpath('//div[@class="pagination"]/a/@href').extract()
        for url in page_list:
            url = response.urljoin(url)
            yield scrapy.Request(url)

    def parse_item(self, response):
        item = TiebaStats()
        thread_count = 0
        post_count = 0
        member_count = 0
        sign_count = 0
        name = re.search(u"forumName:.?'([^']+)',",response.text).group(1)
        if re.search(u'共有主题数<span class="red_text">(\d+)</span>',response.text):
            thread_count = re.search(u'共有主题数<span class="red_text">(\d+)</span>',response.text).group(1)
        elif re.search(u'"?thread_num"?: ?"?(\d+)"?',response.text):
            thread_count = re.search(u'"?thread_num"?: ?"?(\d+)"?',response.text).group(1)
        
        if re.search(u'贴子数.+<span class="red_text">(\d+)</span>篇',response.text,re.S):
            post_count = re.search('贴子数.+<span class="red_text">(\d+)</span>篇',response.text,re.S).group(1)
        
        elif re.search(u'"?post_num"?: ?"?(\d+)"?',response.text):
            post_count = re.search(u'"?post_num"?: ?"?(\d+)"?',response.text).group(1)
            
        elif re.search(u'"?post_num"?: ?"?(\d+)"?',response.text):
            post_count = re.search(u'"?post_num"?: ?"?(\d+)"?',response.text).group(1)
        if re.search(u"'memberNumber': ?'(\d+)',",response.text):
            member_count = re.search(u"'memberNumber': ?'(\d+)',",response.text).group(1)
        elif re.search(u'"memberNumber": ?"(\d+)",',response.text):
            member_count = re.search(u'"memberNumber": ?"(\d+)",',response.text).group(1)
        elif re.search(u'"?member_num"?: ?"?(\d+)"?',response.text):
            member_count = re.search(u'"?member_num"?: ?"?(\d+)"?',response.text).group(1)
        if re.search(u'"current_rank_info":{"sign_count":(\d+),',response.text):
            sign_count = re.search(u'"current_rank_info":{"sign_count":(\d+),',response.text).group(1)
        
        categorymatch = re.search(u'<span>目录：</span>[^<>]+<a[^>]+>([^<>]+)</a>',response.text,re.M)#.group(1)
        if not categorymatch:
            categorymatch = re.search(u'stats-data="area=frs_dir"  target="_blank">([^<>]+)</a>',response.text,re.M)
        if categorymatch:
            category = categorymatch.group(1)
        else:
            category = ''
            
        item['url'] = response.url
        item['name'] = name
        item['category'] = category
        item['thread_count'] = thread_count
        item['post_count'] = post_count
        item['member_count'] = member_count
        item['sign_count'] = sign_count
        item['day'] = str(datetime.today())
        return item