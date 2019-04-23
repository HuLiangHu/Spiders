# -*- coding: utf-8 -*-
import scrapy
import json
import re
from scrapy.conf import settings

from scrapy.selector import Selector
#from .WeiboCookie import copy_cookie



class WeiboCommentsSpider(scrapy.Spider):
    name = "weibocommentinfo"
    ACCESS_TOKEN = settings.get('WEIBO_TOKEN', '2.00ZLWYdC0KWpTWd6c53a1181lvZOiB')
    URL_TEMPLATE = 'https://c.api.weibo.com/2/comments/show/all.json?access_token=%s&id=%s&page=%s&count=100'
    # start_urls=[
    #     'https://weibo.com/3986147355/H1JjaEcTP?type=comment','https://weibo.com/2591595652/H1J0oqhko?type=comment','https://weibo.com/3666565210/H1KeLEo2n?type=comment','https://weibo.com/6223965229/H1KfNelc9?type=comment#_rnd1541731761652','https://weibo.com/2297594122/H1JADzMwx?type=comment','https://weibo.com/3704673325/H1J5X0v5u?filter=hot&root_comment_id=0&type=comment','https://weibo.com/6524663887/H1J1Ag2aY?filter=hot&root_comment_id=0&type=comment'
    # ]
    start_urls = [
        'https://weibo.com/2012292141/HofM81HI6?filter=hot&root_comment_id=0&type=comment#_rnd1554778805369',
        'https://weibo.com/2012292141/Ho73ltsXm?filter=hot&root_comment_id=0&type=comment'
    ]
    # with open('weibo\spiders\weibo.txt', 'r',
    #           encoding='utf-8') as f:
    #     start_urls = f.readlines()

    def __init__(self, *args, **kwargs):
        super(WeiboCommentsSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url)
    def parse(self, response):
        #print(response.text)
        id = re.search('<a name=(\d+) target=',response.text).group(1)
        url ='https://c.api.weibo.com/2/comments/show/all.json?access_token=2.00ZLWYdC0KWpTWd6c53a1181lvZOiB&id={}'.format(id)
        yield scrapy.Request(url,callback=self.parse_item,meta={'url':response.url})
    def parse_item(self, response):
        info = json.loads(response.body)
        commentitem = {}
        commentitem['url'] = response.meta['url']
        commentitem['text'] = info['status']['text']
        commentitem['total_comment_nu mber'] = info['total_number']
        commentitem['reposts_count'] = info['status']['reposts_count']
        commentitem['attitudes_count'] = info['status']['attitudes_count']
        commentitem['publish_time'] = info['status']['created_at']
        commentitem['followers_count'] = info['status']['user']['followers_count']
        commentitem['friends_count'] = info['status']['user']['friends_count']
        commentitem['publisher_profile_url'] = 'https://www.weibo.com' + info['status']['user']['profile_url']
        yield commentitem