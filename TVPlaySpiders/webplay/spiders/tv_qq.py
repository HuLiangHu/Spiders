# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import json
import re
from webplay.items import TVPlayItem
import logging
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.linkextractor import LinkExtractor
from scrapy.spiders.crawl import  Rule,CrawlSpider
class QQSpider(CrawlSpider):
    name = "tv_qq" 
    
    start_urls = [
         'https://v.qq.com/tv/',
        # 'http://v.qq.com/rank/detail/2_-1_-1_-1_2_-1.html',
         'http://v.qq.com/x/list/tv?sort=19&iyear=866&offset=0&iarea=-1',
         'http://v.qq.com/x/list/tv?sort=18&iarea=-1&offset=0',
    ]
    rules = (
        Rule(LinkExtractor(allow=r'https://v.qq.com/x/cover/.*?\.html'),callback='parselink',follow=False),
        Rule(LinkExtractor(allow=r'.*sort=\d+&.*?&offset=\d+'), follow=True)
    )
    def parselink(self, response):

        cover_id = re.search('v.qq.com\/\w\/cover\/(\w+).html', response.url).group(1)
        url = 'http://v.qq.com/detail/%s/%s.html' % (cover_id[0], cover_id)
        yield scrapy.Request(url,callback = self.detail_parse,priority=1,dont_filter = False)

    # def parse(self, response):
    #     if re.match('^(http|https|ftp)\://v.qq.com/tv/',response.url):
    #         for url in response.xpath('//a/@href').extract():
    #             if re.match('^(http|https)\:\/\/v.qq.com\/\w\/cover\/\w+.html',url):
    #                 cover_id = re.search('v.qq.com\/\w\/cover\/(\w+).html',url).group(1)
    #                 url = 'http://v.qq.com/detail/%s/%s.html' %(cover_id[0],cover_id)
    #                 yield scrapy.Request(url,callback = self.detail_parse,priority=1,dont_filter = False)
    #
    #
    #     elif re.match('^(http|https|ftp)\://v.qq.com/x/list/.*',response.url):
    #         coverids = response.xpath('//ul[@class="figures_list"]/li/a/@data-float').extract()
    #         for cover_id in coverids:
    #             url = 'http://v.qq.com/detail/%s/%s.html' %(cover_id[0],cover_id)
    #             yield scrapy.Request(url,callback = self.detail_parse,priority=1,dont_filter = False)
    #         # base_url = get_base_url(response)
    #         #base_url ="http://v.qq.com/x/list/tv"
    #         pages = response.xpath('//div[@class="mod_pages"]/span/a[@class="page_num"]/@href').extract()
    #         for page in pages:
    #             #new_url = base_url+page
    #             # yield scrapy.Request(urljoin_rfc(base_url, page),priority=1,dont_filter = False)
    #             yield response.follow(page,priority=1,dont_filter = False)
    #
    #     elif re.match('^(http|https|ftp)\://v.qq.com/rank/detail/.*',response.url):
    #         urls = response.xpath('//ul[@id="mod_list"]/li/span[@class="mod_rankbox_con_item_title"]/a/@href').extract()
    #         #for  http://film.qq.com/cover/e/ek3kbgy363ka8uk.html
    #         for item in urls:
    #             url = re.sub('/cover/','/detail/',item)
    #             yield scrapy.Request(url,callback = self.detail_parse,priority=1,dont_filter = False)
    #     else:
    #         tvplay = TVPlayItem()
    #         tvplay['url'] = response.url.encode("utf8")
    #         tvplay["aid"] = re.search("id:  '(.+)'",response.text).group(1)
    #         tvplay['cover_img'] = re.search("vpic:  '(.+)'",response.text).group(1)
    #         tvplay['name'] = re.search("title:  '(.+)'",response.text).group(1)
    #         tvplay["website"] = 'qq'
    #         request = scrapy.Request('http://sns.video.qq.com/tvideo/fcgi-bin/batchgetplaymount?low_login=1&id=%s&otype=json'%tvplay['aid'],callback = self.stats_parse,priority=2,dont_filter = False)
    #         request.meta['tvplay'] = tvplay
    #         yield request

    def detail_parse(self,response):

        tvplay = TVPlayItem()
        tvplay['url'] = response.url.encode("utf8")
        if re.search("id:  '(.+)'",response.text):
            tvplay["aid"] = re.search("id:  '(.+)'",response.text).group(1)
        else:
            tvplay["aid"] = re.search("detail\/\w\/([\w]+)",response.url).group(1)
        if re.search("vpic:[ ]+'(.+)';",response.text):
            tvplay['cover_img'] = re.search("vpic:  '(.+)'",response.text).group(1)
        else:
            tvplay['cover_img'] = re.search("vpic:[ ]+'(.+)'",response.text).group(1)
        if re.search("title:  '(.+)'",response.text):
            tvplay['name'] = re.search("title:  '(.+)'",response.text).group(1)
        else:
            tvplay['name'] = re.search("title:[ ]+'(.+)'",response.text).group(1)
        tvplay["website"] = 'qq'
        request = scrapy.Request('http://sns.video.qq.com/tvideo/fcgi-bin/batchgetplaymount?low_login=1&id=%s&otype=json'%tvplay['aid'],callback = self.stats_parse,priority=2,dont_filter = False)
        request.meta['tvplay'] = tvplay
        yield request       
        
    def stats_parse(self,response):
        tvplay = response.meta['tvplay']
        tvplay["playdate" ] =  str(datetime.today())
        if re.search('"all":(\d+)',response.text):
            tvplay['playCount'] = int(re.search('"all":(\d+)',response.text).group(1))
            yield tvplay
        else:
            logging.warning("Cannot get playcount:%s" %str(tvplay))