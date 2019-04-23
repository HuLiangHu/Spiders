# -*- coding: utf-8 -*-
import re
import scrapy
from GcrSpiders.items import U17Item
import json
from scrapy.http import FormRequest
import urllib


class U17spiderSpider(scrapy.Spider):
    name = "u17spider"
    allowed_domains = ["u17.com"]
    start_urls = ['http://www.u17.com/']

    def parse(self, response):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        for i in range(1, 413):  # 450,521
            formdata = {
                'data[group_id]': 'no',
                'data[theme_id]': 'no',
                'data[is_vip]': 'no',
                'data[accredit]': 'no',
                'data[color]': 'no',
                'data[comic_type]': 'no',
                'data[series_status]': 'no',
                'data[order]': '1',
                'data[page_num]': str(i),
                'data[read_mode]': 'no',
                'data[editor_level]': 'no'
            }
            url = "http://www.u17.com/comic/ajax.php?mod=comic_list&act=comic_list_new_fun&a=get_comic_list"

            request = scrapy.Request(url, callback=self.parse_list, headers=headers, method="POST",
                                     body=urllib.parse.urlencode(formdata), dont_filter=True)
            # request.meta['proxy'] = "http://localhost:8888"
            yield request

    def parse_list(self, response):
        listObj = json.loads(response.body_as_unicode())
        for item in listObj['comic_list']:
            url = 'http://www.u17.com/comic/%s.html' % item['comic_id']
            yield scrapy.Request(url, callback=self.detail_page)

    def detail_page(self, response):
        item = U17Item()
        item['site'] = 'u17'
        item['animeid'] = re.search(r'comic\/(\d+)', response.url).group(1)
        item['title'] = response.xpath('//h1[@class="fl"]/text()').extract()[0].strip()
        item['url'] = 'http://www.u17.com/comic/{}.html'.format(item['animeid'])
        item['tags'] = ','.join(response.xpath('//div[@class="top"]/div[@class="line1"]/a/text()').extract())
        info = response.xpath('//div[@class="top"]/div[@class="cf line2"]/div/span/text()').extract()

        item['category'] = info[1].strip()
        item['status'] = info[0].strip()
        item['click_count'] = info[3].strip()
        if u'万' in item['click_count']:
            item['click_count'] = int(float(item['click_count'].replace(u'万', '')) * 10000)
        elif u'亿' in item['click_count']:
            item['click_count'] = int(float(item['click_count'].replace(u'亿', '')) * 100000000)

        item['author'] = response.xpath('//div[@class="author_info"]/div[@class="info"]/a/text()').extract()[0]
        moreinfo = response.xpath('//div[@class="more"]/div[@class="pop_box"]/p/span/em/text()').extract()
        item['monthtickets'] = moreinfo[0]
        item['coll_count'] = moreinfo[1]
        item['tucao_count'] = moreinfo[4]
        item['comment_count'] = moreinfo[5]
        item['recomment_count'] = moreinfo[6]
        item['license_status'] = moreinfo[10].strip()
        return item
        # print(item)
