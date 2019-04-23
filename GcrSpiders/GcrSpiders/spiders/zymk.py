# -*- coding: utf-8 -*-
import re
import scrapy
from GcrSpiders.items import MkItem
import json


class ZYMKSpider(scrapy.Spider):
    name = "zymk"
    allowed_domains = ["zymk.cn/"]
    start_urls = [
        'http://api.zymk.cn/app_api/v3/getallcomic/']

    def parse(self, response):
        jsonList = re.search(',(\[\[.+\]\])',response.body_as_unicode()).group(1)
        #print(jsonList)
        #print(type(jsonList))
        comicList = json.loads(jsonList[0])
        print(comicList)
        for item in comicList:
            print (item)

    def list_page2(self, response):
        for each in response.xpath('//*[@id="toajax"]/li/div[@class="list_content"]/a/@href').extract():
            yield scrapy.Request('http://www.mkzhan.com'+each, callback=self.detail_page)

    def detail_page(self, response):
        item = MkItem()
        item['site'] = 'mk'
        item['title'] = response.xpath('//div[@class="detail-info"]/h3/b/text()').extract_first()
        item['animeid'] = re.search(r'(\d+)', response.url).group(1)
        # class="starting"
        item['license_status'] = '--'
        item['author'] = response.xpath('//div[@class="detail-info"]/p[@class="comic-author"]/span/b/a/text()').extract_first()
        item['rating'] = response.xpath('//div[@class="detail-info"]/div[@class="judge"]/p/text()').extract_first().strip()
        #info = response.xpath('//div[@class="detail-info"]/h3/span/text()').extract()
        item['category'] = response.xpath('//div[@class="detail-info"]/h3/span/text()').extract_first()
        item['recomment_count'] = response.xpath('//p[@class="comic-status"]/span/b/text()').extract()[2]
        item['click_count'] = response.xpath('//p[@class="comic-status"]/span/b/text()').extract()[1]
        #item['recomment_count'] = info[2].replace(u'票', '')
        item['status'] = response.xpath('//div[@class="detail-info"]/p[@class="comic-status"]/span/b/text()').extract_first()
        #item['recomment_count'] = response.xpath('//div[@class="detail-info"]/h3/span/text()').extract_first()
        item['rating_count'] = response.xpath('//div[@class="detail-info"]/div/b/span[@class="score-num"]/text()').extract_first()
        response.xpath('//div[@class="detail-info"]/h3/span/text()').extract()
        item['tags'] = ','.join(response.xpath('//div[@class="detail-info"]/h3/span/text()').extract())

        req = scrapy.Request('http://www.mkzhan.com/comic/comment_list?comic_id=%s&page_num=1&page_size=10' % item['animeid'],
                             callback=self.comment_page)
        req.meta['item'] = item
        yield req

    def comment_page(self, response):
        item = response.meta['item']
        try:
            comments = json.loads(response.text)
            item['comment_count'] = comments['data']['count']
        except:
            item['comment_count'] = 0
        return item
        # print(item)
