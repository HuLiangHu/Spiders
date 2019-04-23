# -*- coding: utf-8 -*-
# __author__ = hul
import scrapy
from urllib.parse import urlencode
from datetime import datetime
from PublicSentimentSpider.items import PublicsentimentspiderItem
from ..simulation_login import simulogin
username = '935718574@qq.com'
password = 'wap662838'

#cookies=simulogin.login(username,password)

class DoubanteamSpider(scrapy.Spider):
    name = 'doubanteam'
    allowed_domains = ['douban.com']
    start_url = 'https://www.douban.com/group/search?'

    groupids = ['248952','589704','394322']
    keyword = '使徒行者'
    cat = 1013

    # 'https://www.douban.com/group/search?cat=1013&group=248952&sort=relevance&q=macbook'
    def start_requests(self):
        headers = {
            'Host': 'www.douban.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
        }
        for groupid in self.groupids:

            parmas = {
                'start': 0,
                'cat': self.cat,
                'group': groupid,
                'sort': 'relevance',
                'q': self.keyword,
            }
            url = self.start_url + urlencode(parmas)
            yield scrapy.Request(url, headers=headers,cookies=cookies)

    def parse(self, response):
        infos = response.xpath('//tr[@class="pl"]')
        for info in infos:
            item = {}
            item['title'] = info.xpath('td[@class="td-subject"]/a/@title').extract_first()
            item['link'] = info.xpath('td[@class="td-subject"]/a/@href').extract_first()
            item['pubtime'] = info.xpath('td[@class="td-time"]/@title').extract_first()
            item['reply'] = info.xpath('td[@class="td-reply"]/span/text()').extract_first()
            headers = {
                'Host': 'www.douban.com',
                'Upgrade-Insecure-Requests': '1',
                'Refere': item['link'],
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
            }

            yield scrapy.Request(item['link'], meta={'item': item}, callback=self.parse_content, headers=headers,cookies=cookies)
        next_page = response.xpath('//span[@class="next"]/a/@href').extract_first()
        print(next_page)
        if next_page:
            yield scrapy.Request(next_page,headers=headers,cookies=cookies)
    def parse_content(self, response):
        item = response.meta['item']
        item['author'] = response.xpath('//span[@class="from"]/a/text()').extract_first()
        item['content'] = '\n'.join(response.xpath('//div[@class="topic-content"]//p/text()').extract())
        item['crawldate'] = str(datetime.now()).split('.')[0]
        yield item