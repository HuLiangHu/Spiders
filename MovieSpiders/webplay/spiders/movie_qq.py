# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import json
import re
from webplay.items import MovieItem
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
import logging
class QQSpider(scrapy.Spider):
    name = "movie_qq" 
    start_urls = ('http://v.qq.com/x/list/movie?sort=18&iarea=-1&offset=0','http://v.qq.com/x/list/dv?sort=18&iarea=-1&offset=0',)

    def parse(self, response):
        if re.match('^(http|https|ftp)\://v.qq.com/x/list/.*',response.url): 
            coverids = response.xpath('//ul[@class="figures_list"]/li/a/@data-float').extract()
            for cover_id in coverids:
                url = 'http://v.qq.com/detail/%s/%s.html' %(cover_id[0],cover_id)
                yield scrapy.Request(url,callback = self.detail_parse,priority=1,dont_filter = False)
            base_url = get_base_url(response)
            pages = response.xpath('//div[@class="mod_pages"]/span/a[@class="page_num"]/@href').extract()
            for page in pages:
                print('*'*100)
                yield scrapy.Request(urljoin_rfc(base_url, page).decode('utf8'),priority=1,dont_filter = False)
        elif re.match('^(http|https|ftp)\://v.qq.com/rank/detail/.*',response.url): 
            urls = response.xpath('//ul[@id="mod_list"]/li/span[@class="mod_rankbox_con_item_title"]/a/@href').extract()
            #for  http://film.qq.com/cover/e/ek3kbgy363ka8uk.html 
            for item in urls:
                url = re.sub('/cover/','/detail/',item)
                yield scrapy.Request(url,callback = self.detail_parse,priority=1,dont_filter = False)
        else:
            tvplay = MovieItem()
            tvplay['url'] = response.url
            tvplay["aid"] = re.search("id:  '(.+)'",response.body_as_unicode()).group(1)
            tvplay['actors'] = ",".join(response.xpath('//ul[@class="actor_list cf"]/li[@itemprop="actor"]/span/text()').extract())
            tvplay['directors'] = ",".join(response.xpath('//ul[@class="actor_list cf"]/li[@itemprop="actor"]/span/text()').extract())
            tvplay['tags'] = ','.join(response.xpath('//div[@class="tag_list"]/a/text()').extract())
            
            tvinfo = response.xpath('//div[@class="detail_video"]/div/div[@class="type_item"]/span[@class="type_txt"]/text()').extract()
            tvplay['area'] = tvinfo[0]
            tvplay['releaseDate'] = tvinfo[-1]
            tvplay['rating'] = response.xpath('//div[@class="video_score"]/div[@class="score_v"]/span[@class="score"]/text()').extract_first()
            if re.search('movie\.douban\.com\/subject\/(\d+)\/',response.body_as_unicode()):
                tvplay['douban'] = re.search('movie\.douban\.com\/subject\/(\d+)\/',response.body_as_unicode()).group(1)
            tvplay['cover_img'] = re.search("vpic:  '(.+)'",response.body_as_unicode()).group(1)
            tvplay['name'] = re.search("title:  '(.+)'",response.body_as_unicode()).group(1)
            tvplay["website"] = 'qq'
            request = scrapy.Request('http://sns.video.qq.com/tvideo/fcgi-bin/batchgetplaymount?low_login=1&id=%s&otype=json'%tvplay['aid'],callback = self.stats_parse,priority=2,dont_filter = False)
            request.meta['tvplay'] = tvplay
            yield request
            
    def detail_parse(self,response):
        tvplay = MovieItem()
        tvplay['url'] = response.url
        tvplay["aid"] = re.search("id:  '(.+)'",response.body_as_unicode()).group(1)
        tvplay['actors'] = ",".join(response.xpath('//ul[@class="actor_list cf"]/li[@itemprop="actor"]/span/text()').extract())
        tvplay['directors'] = ",".join(response.xpath('//ul[@class="actor_list cf"]/li[@itemprop="actor"]/span/text()').extract())
        tvplay['tags'] = ','.join(response.xpath('//div[@class="tag_list"]/a/text()').extract())
        
        tvinfo = response.xpath('//div[@class="detail_video"]/div/div[@class="type_item"]/span[@class="type_txt"]/text()').extract()
        tvplay['area'] = tvinfo[0] 
        tvplay['releaseDate'] = tvinfo[-1]
        tvplay['rating'] = response.xpath('//div[@class="video_score"]/div[@class="score_v"]/span[@class="score"]/text()').extract_first()
        if re.search('movie\.douban\.com\/subject\/(\d+)\/',response.body_as_unicode()):
            tvplay['douban'] = re.search('movie\.douban\.com\/subject\/(\d+)\/',response.body_as_unicode()).group(1)
        tvplay['cover_img'] = re.search("vpic:  '(.+)'",response.body_as_unicode()).group(1)
        tvplay['name'] = re.search("title:  '(.+)'",response.body_as_unicode()).group(1)
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
            