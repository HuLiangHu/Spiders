# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import json
import re
from webplay.items import MovieItem
from scrapy.selector import Selector
import logging
class PPTVSpider(scrapy.Spider):
    name = "movie_pptv"
    #http://epg.api.pptv.com/detail.api?auth=d410fafad87e7bbf6c6dd62434345818&canal=745&userLevel=0&ppi=AQACAAAAAgAATksAAAACAAAAAFb-mwAwLQIVAIp25sfLxaRSSt0MEJofc03-dqTHAhReTdNcCTcs-t0xN5vbJjwRpN-M-Q&appid=com.pplive.androidphone&appver=5.5.0&appplt=aph&vid=9040268&series=1&virtual=1&ver=4&platform=android3&contentType=Preview
    #http://epg.api.pptv.com/list.api?auth=d410fafad87e7bbf6c6dd62434345818&c=30&s=1&vt=21&ver=2&type=2&order=t
    start_urls = ('http://m.pptv.com/sort_list/1------6---1.html',
    )

    def parse(self, response):
        if re.match('^(http|https|ftp)\://m.pptv.com/sort_list/.*',response.url): 
            ids = response.xpath('//dl/dt/a/@href').re(r'http://m.pptv.com/show/(.*).html')
            page = int(re.search('m.pptv.com/sort_list/1------6---(\d+).html',response.url).group(1))
            if len(ids)>=10 or page<300: 
                yield scrapy.Request(re.sub('(\d+).html','%s.html'%(page+1),response.url)) 
            for id in ids:  
                yield scrapy.Request('http://v.pptv.com/show/%s.html'%id,priority=1)
        elif re.match('http://v.pptv.com/show/.*.html',response.url):
            id = response.xpath('//script/text()').re_first('"id":(\d+)')
            yield scrapy.Request('http://epg.api.pptv.com/detail.api?auth=d410fafad87e7bbf6c6dd62434345818&vid=%s'%id,callback = self.albumn_parse,meta = { 'albumnurl':response.url}, priority=2)
        '''
        elif re.match('^(http|https|ftp)\://epg.api.pptv.com/list.api.*',response.url):
            page_count = response.xpath('//vlist/page_count/text()').extract_first()
            countInPage = response.xpath('//vlist/countInPage/text()').extract_first()
            page = response.xpath('//vlist/page/text()').extract_first()
            if page == 1:
                for i in range(2,page_count+1):
                    url = re.sub('s=1','s=%s' %i,response.url)
                    yield scrapy.Request(url,priority=1)
            for item in response.xpath('//vlist/v'):
                id = item.xpath('vid/text()').extract_first()
                yield scrapy.Request('http://epg.api.pptv.com/detail.api?auth=d410fafad87e7bbf6c6dd62434345818&vid=%s' %id,callback = self.albumn_parse,priority=1)
        '''
            
    def albumn_parse(self,response):
        tvplay = MovieItem() 
        tvplay["url"] = response.meta['albumnurl']
        tvplay["website"] = 'pptv'
        tvplay['name'] = response.xpath('//title/text()').extract_first()
        tvplay['aid'] = response.xpath('//vid/text()').extract_first()
        tvplay['area'] = response.xpath('//area/text()').extract_first()
        tvplay['desc'] = response.xpath('//content/text()').extract_first()
        tvplay['directors'] = response.xpath('//director/text()').extract_first()
        tvplay['actors'] = response.xpath('//act/text()').extract_first()
        tvplay['cover_img'] = response.xpath('//imgurl/text()').extract_first()
        tvplay['playdate'] = str(datetime.today())
        tvplay['playCount'] = response.xpath('//pv/text()').extract_first()
        if len(response.xpath('//fixupdate/text()').extract())!=0:
            tvplay['playStatus'] = response.xpath('//fixupdate/text()').extract_first()
        else:
            tvplay['playStatus'] =''
        tvplay['genre'] = response.xpath('//catalog/text()').extract_first()
        
        tvplay['releaseDate'] = response.xpath('//onlinetime/text()').extract_first()
        
        yield tvplay
        #yield tvplay