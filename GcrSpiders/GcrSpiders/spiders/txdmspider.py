# -*- coding: utf-8 -*-
import re
import json
import scrapy
from GcrSpiders.items import TxdmItem

class TxdmspiderSpider(scrapy.Spider):
    name = "txdmspider"
    allowed_domains = ["ac.qq.com"]
    # start_urls = ['http://ac.qq.com/Comic/all/search/time/page/1']

    def start_requests(self):
        # //*[@id="pagination2"]/a[5]
        total_page = 1000
        for i in range(total_page):
            next_url = 'https://ac.qq.com/Comic/all/search/time/page/%s' % (i+1)
            yield scrapy.Request(next_url, callback=self.list_page)

    def list_page(self, response):
        for url in response.xpath('//h3/a/@href').extract():
            yield scrapy.Request('https://ac.qq.com' + url, callback=self.detail_page)
    # def start_requests(self):
    #     yield scrapy.Request('https://ac.qq.com/Comic/comicInfo/id/17114', callback=self.detail_page)
    def detail_page(self, response):
        item = TxdmItem()
        item['site'] = 'txdm'
        item['title'] = response.xpath('//h2/strong/text()').extract()[0]
        try:
            item['rating'] = response.xpath('//strong[@class="ui-text-orange"]/text()').extract()[0]
        except:
            item['rating'] = -1
        item['animeid'] = response.xpath('//*[@id="input_id"]/@value').extract()[0]
        item['url'] = 'https://ac.qq.com/Comic/ComicInfo/id/{}'.format(item['animeid'])
        item['rating_count'] = response.xpath('//p[@class="ui-left"]/span/text()').extract()[0]
        item['author'] = response.xpath('//span[@class="first"]/em/text()').extract()[0].replace(u'\xa0', '')
        item['coll_count'] = response.xpath('//em[@id="coll_count"]/text()').extract()[0]
        item['click_count'] = re.search(u'<span>人气：<em>([^<]+)</em></span>', response.text).group(1).replace(',', '')
        item['status'] = response.xpath('//*[@id="special_bg"]/div[3]/div[1]/div[1]/div[1]/label/text()').extract()[0]
        item['tags'] = ' '.join(response.xpath('//div[@id="special_bg"]/div/p/a[@target="_blank"]/@title').extract())
        if u'万' in item['click_count']:
            item['click_count'] = int(float(item['click_count'].replace(u'万', ''))*10000)
        elif u'亿' in item['click_count']:
            item['click_count'] = int(float(item['click_count'].replace(u'亿', ''))*100000000)
        try:
            item['tucao_count'] = re.search(u'<span>吐槽：<em>([^<]+)</em></span>', response.text).group(1)
        except:
            item['tucao_count'] = 0
        item['redtickets'] = response.xpath('//strong[@id="redcount"]/text()').extract()[0]
        # //*[@id="special_bg"]/div[3]/div[1]/div[2]/ul/li[2]/strong
        item['blacktickets'] = response.xpath('//*[@id="special_bg"]/div[3]/div[1]/div[2]/ul/li[2]/strong/text()').extract()[0]
        headers = {
            'Host': 'ac.qq.com',
            'Referer': 'https://ac.qq.com/Comic/comicInfo/id/{}'.format(item['animeid']),
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
        }
        req = scrapy.Request('https://ac.qq.com/Community/topicList?targetId={}'.format(item['animeid']),
                             callback=self.comment_page, headers=headers)
        req.meta['item'] = item
        yield req

    # def tag_page(self,response):
    #     item = response.meta['item']
    #     tags = ' '.join([tag['name'] for tag in json.loads(response.text)['tag']])
    #     item['tags'] = tags
    #
    #     #http://ac.qq.com/Comic/userComicInfo?comicId=46
    #     headers ={
    #         'Host': 'ac.qq.com',
    #         'Referer': 'https://ac.qq.com/Comic/comicInfo/id/{}'.format(item['animeid']),
    #         'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    #     }
    #     req = scrapy.Request('https://ac.qq.com/Community/topicList?targetId={}'.format(item['animeid']),
    #                          callback=self.comment_page,headers=headers)
    #     req.meta['item'] = item
    #     yield req

    def comment_page(self,response):

        item = response.meta['item']
        try:
            item['comment_count'] = re.search(r'<em class="commen-ft-ts">(\d+)</em>', response.text).group(1)
        except:
            item['comment_count'] = 0
        return item
        # print(item)
