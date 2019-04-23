# -*- coding: utf-8 -*-
import re
import scrapy
from GcrSpiders.items import MkItem
import json
import requests


class MkspiderSpider(scrapy.Spider):
    name = "mkspider"
    allowed_domains = ["mkzhan.com"]
    start_urls = ['https://www.mkzhan.com/category/']

    def parse(self, response):
        next_page = response.xpath('//div/a[@class="next"]/@href').extract_first()
        yield scrapy.Request('https://www.mkzhan.com/'+next_page)


        for sel in response.xpath("//a[@class='cover']/@href").extract():
            #detailurl = sel.xpath('div[2]/a/@href').extract()[0]
            #print('https://www.mkzhan.com'+sel)
            yield scrapy.Request('https://www.mkzhan.com'+sel, callback=self.detail_page)

    # def list_page2(self, response):
    #     for each in response.xpath('//*[@id="toajax"]/li/div[@class="list_content"]/a/@href').extract():
    #         yield scrapy.Request('https://www.mkzhan.com'+each, callback=self.detail_page)
    # def start_requests(self):
    #     url='https://www.mkzhan.com/208701/'
    #     yield scrapy.Request(url,callback=self.detail_page)
    def detail_page(self, response):
        item = MkItem()
        item['site'] = 'mk'
        item['title'] = response.xpath('/html/body/div[1]/div[3]/div/p[1]/text()').extract_first()
        item['animeid'] = re.search(r'(\d+)', response.url).group(1)
        #print(item['animeid'])
        # class="starting"
        item['url'] = 'https://www.mkzhan.com/{}/'.format(item['animeid'])
        item['license_status'] = '--'
        item['author'] = response.xpath("//span[@class='name']/a/text()").extract_first()
        item['rating'] = float(int(re.findall('<.*data-score="(.*?)">',response.text)[0])/10)

        #info = response.xpath('//div[@class="detail-info"]/h3/span/text()').extract()
        item['category'] = response.xpath('//span[@class="text"][1]/b/text()').extract_first()
        coll_count = response.xpath('//span[@class="text"][2]/b/text()').extract_first()
        item['coll_count'] = self.str2float(coll_count)
        click_count = response.xpath('//span[@class="text"][3]/b/text()').extract_first()
        item['click_count']=self.str2float(click_count)
        item['recomment_count'] = 0
        #item['coll_count'] =  response.xpath('//div[@class="detail-info"]/p[@class="comic-status"]/span/b/text()').extract_first()
        item['status'] = response.xpath('/html/body/div[2]/div[1]/div[1]/div[1]/span[2]/text()').extract_first()
        if '停更' in item['status']:
            item['status']='停更'
        else:
            item['status']='连载中'
        #item['recomment_count'] = response.xpath('//div[@class="detail-info"]/h3/span/text()').extract_first()
        item['rating_count'] = response.xpath('//p[@class="rate-count"]/span[@class="num"]/text()').extract_first()
        #response.xpath('//div[@class="detail-info"]/h3/span/text()').extract()
        item['tags'] = ','.join(response.xpath('//span[@class="text"][1]/b/text()').extract())
        #print(item['tags'])

        req = scrapy.Request('https://comment.mkzhan.com/comment/?comic_id=%s&page_num=1&page_size=10' % item['animeid'],
                             callback=self.comment_page)
        #print(item)
        req.meta['item'] = item
        yield req
        #print(req)
    # comment_count = scrapy.Field()
    # recomment_count = scrapy.Field()

    def comment_page(self, response):
        #print(response.text)
        item = response.meta['item']
        #print(item)
        try:
            comments = json.loads(response.text)
            item['comment_count'] = comments['data']['count']
        except:
            item['comment_count'] = 0
        yield item
        #print(item)
    def str2float(self,data):
        if '万' in data:
            data = float(re.sub('万', '', data)) * 10000
        elif '亿' in data:
            data = float(re.sub('亿', '', data)) * 100000000

        else:
            data = data
        return round(data)