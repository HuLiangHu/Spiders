# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import json
import re
from variety.items import VarietyItem,VarietyVideoItem
from scrapy.selector import Selector

class PPTVSpider(scrapy.Spider):
    name = "variety_pptv"
    #http://epg.api.pptv.com/detail.api?auth=d410fafad87e7bbf6c6dd62434345818&canal=745&userLevel=0&ppi=AQACAAAAAgAATksAAAACAAAAAFb-mwAwLQIVAIp25sfLxaRSSt0MEJofc03-dqTHAhReTdNcCTcs-t0xN5vbJjwRpN-M-Q&appid=com.pplive.androidphone&appver=5.5.0&appplt=aph&vid=9040268&series=1&virtual=1&ver=4&platform=android3&contentType=Preview
    #http://epg.api.pptv.com/list.api?auth=d410fafad87e7bbf6c6dd62434345818&c=30&s=1&vt=21&ver=2&type=2&order=t
    start_urls = ('http://m.pptv.com/sort_list/4------1---100.html',
    )

    def parse(self, response):
        if re.match('^(http|https|ftp)\://m.pptv.com/sort_list/.*',response.url): 
            ids = response.xpath('//dl/dt/a/@href').re(r'http://m.pptv.com/show/(.*).html')
            page = int(re.search('m.pptv.com/sort_list/4------1---(\d+).html',response.url).group(1))
            if len(ids)>0: 
                yield scrapy.Request(re.sub('(\d+).html','%s.html'%(page+1),response.url))
            for id in ids:
                #yield scrapy.Request()
                yield scrapy.Request('http://v.pptv.com/page/%s.html'%id,priority=1)
        elif re.match('http://v.pptv.com/page/.*.html',response.url):
            id = response.xpath('//script/text()').re_first('"id":(\d+)')
            yield scrapy.Request('http://epg.api.pptv.com/detail.api?auth=d410fafad87e7bbf6c6dd62434345818&vid=%s'%id,callback = self.albumn_parse,meta = { 'albumnurl':response.url}, priority=2)
        '''
        elif re.match('^(http|https|ftp)\://epg.api.pptv.com/list.api.*',response.url):
            count = response.xpath('//vlist/count/text()').extract_first()
            countInPage = response.xpath('//vlist/countInPage/text()').extract_first()
            page = response.xpath('//vlist/page/text()').extract_first()
            for item in response.xpath('//vlist/v'):
                id = item.xpath('vid/text()').extract_first()
                yield scrapy.Request('http://epg.api.pptv.com/detail.api?auth=d410fafad87e7bbf6c6dd62434345818&vid=%s' %id,callback = self.albumn_parse,priority=1,dont_filter = True)
        '''        
            
    def albumn_parse(self,response):
        tvplay = VarietyItem() 
        tvplay["url"] = response.meta['albumnurl']
        tvplay["website"] = 'pptv'
        tvplay['name'] = response.xpath('//title/text()').extract_first()
        tvplay['aid'] = response.xpath('//vid/text()').extract_first()
        tvplay['area'] = response.xpath('//area/text()').extract_first()
        tvplay['desc'] = response.xpath('//content/text()').extract_first() 
         
         
        tvplay['playdate'] = str(datetime.today())
        tvplay['playCount'] = response.xpath('//pv/text()').extract_first()
        tvplay['playStatus'] = response.xpath('//fixupdate/text()').extract_first()
        tvplay['category'] = response.xpath('//catalog/text()').extract_first()
        tvplay['lastseries'] = response.xpath('//vsTitle/text()').extract_first()
        tvplay['releaseDate'] = response.xpath('//onlinetime/text()').extract_first() 
        yield tvplay
        
        videos = response.xpath('//video_list/video')
        for video in videos:
            videoItem = VarietyVideoItem()
            videoItem['url'] = video.xpath('text()').extract_first()
            videoItem['aid'] = tvplay['aid']
            videoItem["website"] = 'pptv'
            videoItem['vid'] = video.xpath('@id').extract_first()
            videoItem['albumurl'] = tvplay["url"]
            videoItem['playdate'] = str(datetime.today())
            videoItem['playCount'] = video.xpath('@pv').extract_first()
            videoItem['video_img'] = video.xpath('@sloturl').extract_first()
            videoItem['name'] = video.xpath('@title').extract_first()
            videoItem['releaseDate'] = video.xpath('@createTime').extract_first()
            videoItem['episode'] = video.xpath('@date').extract_first()
            videoItem['duration'] = video.xpath('@durationSecond').extract_first()
            yield videoItem
        #http://v.pptv.com/show/videoList?pid=969341    
        #yield tvplay