# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import json
import re
from webplay.items import TVPlayItem
class TudouSpider(scrapy.Spider):
    name = "tv_tudou" 
      
    start_urls = ['http://www.tudou.com/s3portal/service/pianku/data.action?pageSize=90&app=mainsitemobile&deviceType=1&tags=&tagType=3&firstTagId=3&areaCode=310000&initials=&hotSingerId=&pageNo=1&sortDesc=quality']
    MAX_PAGE = 0
    def parse(self, response):
        if re.match('^(http|https|ftp)\://www.tudou.com/s3portal/service.*',response.url): 
            listObj  = json.loads(response.body_as_unicode())
            page = int(re.search('pageNo=(\d+)',response.url).group(1))
            page_size = int(re.search('pageSize=(\d+)',response.url).group(1))
            if self.MAX_PAGE == 0: 
                self.MAX_PAGE = listObj['total']/page_size if listObj['total']%page_size == 0 else listObj['total']/page_size + 1 
            if len(listObj['items']) > 0 or page<= self.MAX_PAGE:
                url = re.sub('pageNo=(\d+)','pageNo=%s' % (page + 1),response.url) 
                yield scrapy.Request(url,dont_filter = False)
            for item in listObj['items']:
                tvplay = TVPlayItem()
                tvplay["website"] = "tudou"
                tvplay["url"] =  item['playUrl'].replace('albumplay','albumcover')
                #tvplay["playUrl"] =  item['playUrl']
                tvplay["alias"] = item['alias']
                tvplay["aid"] = item['albumId']
                tvplay["actors"] = ','.join([actor['name'] for actor in item['actors']])
                #"episodes"] = item['total_video_count'],
                tvplay["playStatus"] = item['updateInfo']
                #"publist_time"] = item['publish_time'],
                #"category"] = item['second_cate_name'],
                #"tag"] = item['albumDocInfo']['albumTitle']
                tvplay["desc"] = item['albumShortDesc']
                tvplay["name"] = item['title']              
                tvplay["playCount"] = item['playtimes']
                tvplay["cover_img_sm"] = item["picUrl_200x112"]
                tvplay["cover_img"] = item["picUrl_448x672"]
                tvplay["playdate" ] =  str(datetime.today())
                #"videoType":item['albumDocInfo']['channel'] 
                yield tvplay
        else:
            tvplay = TVPlayItem()
            tvplay["website"] = "tudou"
            tvplay["url"] =  response.url
            tvplay['aid'] = re.search("aid: '(\d+)',",response.body_as_unicode()).group(1)
            tvplay["name"] =  re.search("title: '(.+)',",response.body_as_unicode()).group(1)
            request = scrapy.Request('http://index.youku.com/dataapi/getData?sid=%s&num=100007'%tvplay['aid'],callback = self.stats_parse,dont_filter = False)
            request.meta['tvplay'] = tvplay
            yield request
            
    def stats_parse(self,response):
        tvplay = response.meta['tvplay']
        tvplay["playdate" ] =  str(datetime.today())
        tvplay['playCount'] = int(re.search('"vv":(\d+)',response.body_as_unicode()).group(1))
        yield tvplay
           
