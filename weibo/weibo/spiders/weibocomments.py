# -*- coding: utf-8 -*-
import scrapy
import json
import re
from scrapy.conf import settings

from scrapy.selector import Selector


class WeiboCommentsSpider(scrapy.Spider):
    name = "weibocomments"
    ACCESS_TOKEN = settings.get('WEIBO_TOKEN', '2.00ZLWYdC0KWpTW73ca4f3acb4k45rD')
    URL_TEMPLATE = 'https://c.api.weibo.com/2/comments/show/all.json?access_token=%s&id=%s&page=%s&count=100'
    start_urls=[
        'https://weibo.com/3986147355/H1JjaEcTP?type=comment','https://weibo.com/2591595652/H1J0oqhko?type=comment','https://weibo.com/3666565210/H1KeLEo2n?type=comment','https://weibo.com/6223965229/H1KfNelc9?type=comment#_rnd1541731761652','https://weibo.com/2297594122/H1JADzMwx?type=comment','https://weibo.com/3704673325/H1J5X0v5u?filter=hot&root_comment_id=0&type=comment','https://weibo.com/6524663887/H1J1Ag2aY?filter=hot&root_comment_id=0&type=comment'
    ]
    def __init__(self, *args, **kwargs):
        super(WeiboCommentsSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        #self._increment_status_code_stat(response)
        redirect_urls = response.request.meta['redirect_urls']
        ori_url = None
        if len(redirect_urls)>0:
            ori_url = redirect_urls[0]
        requrl = response.request.url 
        if re.search('((http|https):\/\/)api\.weibo\.com\/2\/statuses', requrl):
            jsonObj = json.loads(response.body)
            weibo_id = jsonObj['id']
            url = self.URL_TEMPLATE % (self.ACCESS_TOKEN,weibo_id,1)
            req = scrapy.Request(url, meta=response.meta, callback = self.parse)
            req.meta['weibo_id'] = weibo_id
            req.meta['page'] = 1
            yield req

        elif re.search('((http|https):\/\/)weibo\.cn\/\w+\/\w+', requrl):
            domain = re.search('weibo\.cn\/\w+\/(\w+)', requrl).group(1) 
            url = 'https://api.weibo.com/2/statuses/queryid.json?access_token=%s&mid=%s&type=1&isBase62=1' % (self.ACCESS_TOKEN,domain)
            req = scrapy.Request(url, meta=response.meta, callback = self.parse)
            req.meta['url'] = requrl
            yield req

        elif re.search('((http|https):\/\/)c\.api\.weibo\.com\/2\/comments', requrl):
            # page = re.search('page=(\d+)', requrl).group(1)
             
            info = json.loads(response.body)
            if re.search('page=1&', requrl):
                weibo_id = response.meta['weibo_id']
                totalpage = int(info['total_number']/100 if info['total_number'] % 100 == 0 else info['total_number'] / 100 + 1)
                 
                for i in range(2, totalpage):
                    url = self.URL_TEMPLATE % (self.ACCESS_TOKEN,weibo_id,i)
                    req = scrapy.Request(url, meta=response.meta, callback = self.parse)
                    yield req

            for comment in info['comments']:
                try:
                    commentitem = {}
                    commentitem['url'] = response.meta['url']
                    commentitem['id'] = comment['id']
                    try:
                        commentitem['weibo_url'] = response.meta['url']
                    except:
                        commentitem['weibo_url'] = requrl
                    commentitem['created_at'] = comment['created_at']
                    re_emoji = re.compile(u'[^\u0000-\uD7FF\uE000-\uFFFF]')
                    try:
                        source = ' '.join(Selector(text=comment['source']).xpath('//text()').extract())
                        commentitem['source'] = re_emoji.sub(' ', source)
                    except Exception as e:
                        commentitem['source'] = ""
                    commentitem['source'] = ""
                    commentitem['userid'] = comment['user']['id']
                    commentitem['screen_name'] = comment['user']['screen_name']
                    commentitem['text'] = re_emoji.sub(' ', comment['text'])
                    yield commentitem
                except Exception as e:
                    print(e)
                    
        elif ori_url and re.search('((http|https):\/\/)weibo\.com\/\w+\/\w+', ori_url):
            domain = re.search('weibo\.com\/\w+\/(\w+)', ori_url).group(1)
            url = 'https://api.weibo.com/2/statuses/queryid.json?access_token=%s&mid=%s&type=1&isBase62=1' % (self.ACCESS_TOKEN,domain)
            req = scrapy.Request(url, meta=response.meta, callback = self.parse)
            req.meta['url'] = ori_url
            yield req
