# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import json
import re
from webplay.items import TVPlayItem
from scrapy.selector import Selector
class PPTVSpider(scrapy.Spider):
    name = "tv_pptv"
        
    #http://epg.api.pptv.com/detail.api?auth=d410fafad87e7bbf6c6dd62434345818&canal=745&userLevel=0&ppi=AQACAAAAAgAATksAAAACAAAAAFb-mwAwLQIVAIp25sfLxaRSSt0MEJofc03-dqTHAhReTdNcCTcs-t0xN5vbJjwRpN-M-Q&appid=com.pplive.androidphone&appver=5.5.0&appplt=aph&vid=9040268&series=1&virtual=1&ver=4&platform=android3&contentType=Preview
    #http://epg.api.pptv.com/list.api?auth=d410fafad87e7bbf6c6dd62434345818&c=30&s=1&vt=21&ver=2&type=2&order=t
    start_urls = [
        'http://m.pptv.com/cate_list/pg_m_list?type=2&vip=0&page=1&order=n',
        'http://m.pptv.com/sort_list/2------6---1.html',
        'http://list.pptv.com/channel_list.html?page=1&type=211262&sort=time&attribute=211262',
        'http://list.pptv.com/channel_list.html?page=1&type=2&sort=1&pay=0',
        'http://list.pptv.com/channel_list.html?page=1&type=2&sort=1'
    ]
    custom_settings = {
        "DOWNLOAD_DELAY" : 0.3
    }
    def parse(self, response):
        if re.match('^(http|https|ftp)\://m.pptv.com/sort_list/.*',response.url): 
            ids = response.xpath('//dl/dt/a/@href').re(r'http://m.pptv.com/show/(.*).html')
            page = int(re.search('m.pptv.com/sort_list/2------6---(\d+).html',response.url).group(1))
            if len(ids)>=15 and page<200: 
                yield scrapy.Request(re.sub('(\d+).html','%s.html'%(page+1),response.url),dont_filter = False)
            for id in ids:
                #yield scrapy.Request()
                yield scrapy.Request('http://v.pptv.com/page/%s.html'%id,priority=1,dont_filter = False)
        elif re.match('^(http|https|ftp)\:\/\/list.pptv.com\/channel_list.html',response.url):
            #ul>li>p>a.detailbtn
            urls = response.xpath('//li/p/a[@class="detailbtn"]/@href').extract()
            if len(urls)>=20:
                page = int(re.search('page=(\d+)',response.url).group(1))
                next_page = re.sub('page=\d+','page=%s' %(page+1),response.url)
                yield scrapy.Request(next_page,priority=1,dont_filter = False)
            for url in urls:
                yield scrapy.Request(url,priority=1,dont_filter = False)
        elif re.match('^(http|https|ftp)\:\/\/m.pptv.com\/cate_list\/pg_m_list',response.url):
            #ul>li>p>a.detailbtn
            items = json.loads(response.body_as_unicode())
            page = int(items['result']['page_count'])
            if re.search('page=1&',response.url):
                for i in range(2,page+1):
                    next_page = re.sub('&page=1','&page=%s' %i,response.url)
                    yield scrapy.Request(next_page,priority=1,dont_filter = False)
            for item in items['result']['data']:
                id = re.search('http://m.pptv.com/show/(.*).html',item['link']).group(1)
                yield scrapy.Request('http://v.pptv.com/page/%s.html'%id,priority=1,dont_filter = False)
        elif re.match('http://v.pptv.com/page/.*.html',response.url):
            id = response.xpath('//script/text()').re_first('"id":(\d+)')
            yield scrapy.Request('http://epg.api.pptv.com/detail.api?auth=d410fafad87e7bbf6c6dd62434345818&vid=%s'%id,callback = self.albumn_parse,meta = { 'albumnurl':response.url}, priority=2,dont_filter = False)
        '''
        elif re.match('^(http|https|ftp)\://epg.api.pptv.com/list.api.*',response.url):
            count = response.xpath('//vlist/count/text()').extract_first()
            countInPage = response.xpath('//vlist/countInPage/text()').extract_first()
            page = response.xpath('//vlist/page/text()').extract_first()
            for item in response.xpath('//vlist/v'):
                id = item.xpath('vid/text()').extract_first()
                yield scrapy.Request('http://epg.api.pptv.com/detail.api?auth=d410fafad87e7bbf6c6dd62434345818&vid=%s' %id,callback = self.albumn_parse,priority=1,dont_filter = False)
        '''        
            
    def albumn_parse(self,response):
        tvplay = TVPlayItem() 
        tvplay["url"] = response.meta['albumnurl']
        tvplay["website"] = 'pptv'
        tvplay['name'] = response.xpath('//title/text()').extract_first()
        tvplay['aid'] = response.xpath('//vid/text()').extract_first()
        tvplay['area'] = response.xpath('//area/text()').extract_first()
        tvplay['desc'] = response.xpath('//content/text()').extract_first()
        tvplay['episodes'] = response.xpath('//total_state/text()').extract_first()
        tvplay['directors'] = response.xpath('//director/text()').extract_first()
        tvplay['actors'] = response.xpath('//act/text()').extract_first()
        tvplay['cover_img'] = response.xpath('//imgurl/text()').extract_first()
        tvplay['playdate'] = str(datetime.today())
        tvplay['playCount'] = response.xpath('//pv/text()').extract_first()
        tvplay['playStatus'] = response.xpath('//fixupdate/text()').extract_first()
        tvplay['genre'] = response.xpath('//catalog/text()').extract_first()
        tvplay['lastepisode'] = response.xpath('//video_list_count/text()').extract_first()
        tvplay['releaseDate'] = response.xpath('//onlinetime/text()').extract_first()
        
        yield tvplay
        #yield tvplay