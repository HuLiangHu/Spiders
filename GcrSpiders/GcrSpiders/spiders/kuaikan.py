# -*- coding: utf-8 -*-
import scrapy
import json
import time
from datetime import datetime
import re

from GcrSpiders.items import KKItem


class KuaikanSpider(scrapy.Spider):
    name = 'kuaikan'
    #allowed_domains = ['kuaikanmanhua.com']
    start_urls = 'https://api.kkmh.com/v1/topic_new/lists/get_by_tag?count=20&since={}&tag=0&gender=0&sort=1&query_category=%7B%0A%20%20%22pay_status%22%20%3A%20-1%2C%0A%20%20%22update_status%22%20%3A%20-1%0A%7D'
    Appapi ='https://api.kkmh.com/v1/topics/{}?is_homepage=0&is_new_device=false&page_source=17&sort=0&sortAction=0'

    def start_requests(self):
        for page in range(125):
            url =self.start_urls.format(page*20)
            yield scrapy.Request(url,dont_filter=True)

    def parse(self, response):

        for i in json.loads(response.text)['data']['topics']:
            item =KKItem()

            item['title'] =i['title']
            item['author'] = i['user']['nickname']
            item['animeid'] =i['id']

            url =self.Appapi.format(item['animeid'])
            headers ={
                'Host': 'api.kkmh.com',
                'User-Agent': 'Kuaikan/5.13.5/513005(iPhone;iOS 12.1;Scale/2.00;WiFi;1334*750)'
            }
            yield scrapy.Request(url,headers=headers,meta={'item':item},callback=self.parse_comment,dont_filter=True)

    def parse_comment(self, response):
        item = response.meta['item']
        data = json.loads(response.text)['data']
        item['url'] = 'https://www.kuaikanmanhua.com/web/topic/{}'.format(item['animeid'])
        item['likes'] = data['likes_count']  # 点赞数
        item['status'] = data['update_status']
        item['comics_count'] = data['comics_count']
        item['comment_count'] = data['comments_count']
        item['category'] = ';'.join(data['category'])
        item['tags'] = item['category']
        item['click_count'] = data['view_count']  # 热度
        item['coll_count'] = data['fav_count']  # 关注人数
        item['site'] = 'kuaikan'
        item['renqi'] = data['popularity_value']  # 人气值
        yield item


