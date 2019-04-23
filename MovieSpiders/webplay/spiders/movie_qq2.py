# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import json
import re
from webplay.items import MovieItem
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
import logging
class QQSpider2(scrapy.Spider):
    name = "movie_qq2" 
    start_urls = ('http://v.qq.com/x/list/movie?offset=0&format=2&iarea=-1&sort=18',)

    def parse(self, response):
        if re.match('^(http|https|ftp)\://v.qq.com/x/list/.*',response.url): 
            urls = response.xpath('//ul[@class="figures_list"]/li/a/@href').extract()
            for url in urls:
                yield scrapy.Request(url,callback = self.detail_parse,priority=1,dont_filter = False)
            base_url = get_base_url(response)
            pages = response.xpath('//div[@class="mod_pages"]/span/a[@class="page_num"]/@href').extract()
            for page in pages:
                yield scrapy.Request(urljoin_rfc(base_url, page).decode('utf8'),priority=1,dont_filter = False)
        else:
            tvplay = MovieItem()
            cover_str = re.search('var COVER_INFO = ({.+})',response.body_as_unicode()).group(1)
            cover_info = json.loads(cover_str)
            
            tvplay["aid"] = cover_info['id']
            tvplay['url']  = 'https://v.qq.com/detail/%s/%s.html' %(tvplay["aid"][0],tvplay["aid"])
            tvplay['actors'] = ",".join(cover_info['leading_actor'])
            tvplay['directors'] = ",".join(cover_info['director'])
            if cover_info['sub_genre']:
                tvplay['tags'] = ','.join(cover_info['sub_genre'])
            tvplay['timeLength'] = re.search('"duration":"(\d+)"',response.body_as_unicode()).group(1)
             
            tvplay['area'] = cover_info['area_name']
            tvplay['releaseDate'] = cover_info['publish_date']
            tvplay['rating'] = cover_info['score']['score']
            #tvplay['douban'] = re.search('movie\.douban\.com\/subject\/(\d+)\/',response.body_as_unicode()).group(1)
            tvplay['cover_img'] = cover_info['vertical_pic_url']
            tvplay['name'] = cover_info['series_name']
            tvplay["website"] = 'qq'
            request = scrapy.Request('http://sns.video.qq.com/tvideo/fcgi-bin/batchgetplaymount?low_login=1&id=%s&otype=json'%tvplay['aid'],callback = self.stats_parse,priority=2,dont_filter = False)
            request.meta['tvplay'] = tvplay
            yield request
            
    def detail_parse(self,response):
        tvplay = MovieItem()
        cover_str = re.search('var COVER_INFO = ({.+})',response.body_as_unicode()).group(1)
        cover_info = json.loads(cover_str)
        
        tvplay["aid"] = cover_info['id']
        tvplay['url']  = 'https://v.qq.com/detail/%s/%s.html' %(tvplay["aid"][0],tvplay["aid"])
        tvplay['actors'] = ",".join(cover_info['leading_actor'])
        tvplay['directors'] = ",".join(cover_info['director'])
        if cover_info['sub_genre']:
            tvplay['tags'] = ','.join(cover_info['sub_genre'])
        tvplay['timeLength'] = re.search('"duration":"(\d+)"',response.body_as_unicode()).group(1)
            
        tvplay['area'] = cover_info['area_name']
        tvplay['releaseDate'] = cover_info['publish_date']
        tvplay['rating'] = cover_info['score']['score']
        #tvplay['douban'] = re.search('movie\.douban\.com\/subject\/(\d+)\/',response.body_as_unicode()).group(1)
        tvplay['cover_img'] = cover_info['vertical_pic_url']
        tvplay['name'] = cover_info['series_name']
        tvplay["website"] = 'qq'
        request = scrapy.Request('http://sns.video.qq.com/tvideo/fcgi-bin/batchgetplaymount?low_login=1&id=%s&otype=json'%tvplay['aid'],callback = self.stats_parse,priority=2,dont_filter = False)
        request.meta['tvplay'] = tvplay
        yield request
        
    def stats_parse(self,response):
        tvplay = response.meta['tvplay']
        tvplay["playdate" ] =  str(datetime.today())
        tvplay['playCount'] = int(re.search('"all":(\d+)',response.body_as_unicode()).group(1))
        yield tvplay
        '''
        request = scrapy.Request('https://ncgi.video.qq.com/fcgi-bin/video_comment_id?otype=json&op=3&cid=%s'% tvplay['aid'],callback = self.commentid_parse ,priority =3 )
        request.meta['tvplay'] = tvplay
        yield request
        '''
    def commentid_parse(self,response):
        tvplay = response.meta['tvplay']
        commentid = re.search('"comment_id":"(\d+)"',response.body_as_unicode()).group(1)
        request = scrapy.Request('https://coral.qq.com/article/%s/commentnum' %commentid,callback = self.commentcount_parse ,priority =4 )
        request.meta['tvplay'] = tvplay
        yield request

    def commentcount_parse(self,response):
        tvplay = response.meta['tvplay'] 
        tvplay['commentcount'] = int(re.search('"commentnum":"(\d+)"',response.body_as_unicode()).group(1))
        yield tvplay
            