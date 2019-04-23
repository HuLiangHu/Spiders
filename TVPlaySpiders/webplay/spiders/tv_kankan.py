# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import json
import re
from random import choice 
from webplay.items import TVPlayItem
class KankanSpider(scrapy.Spider):
    name = "tv_kankan" 
    custom_settings = {
        "DOWNLOAD_DELAY": 1
    }
    #'http://list.pad.kankan.com/common_mobile_list/act,1/type,teleplay/os,az/osver,5.1/productver,5.0.0.16/genre,_ALL_/sort,hits/genre,_ALL_/year,_ALL_/area,_ALL_/status,_ALL_/page,2/pernum,200/'
    start_urls = ['http://list.pad.kankan.com/common_mobile_list/act,1/type,teleplay/os,az/osver,5.1/productver,5.0.0.16/genre,_ALL_/sort,hits/genre,_ALL_/year,_ALL_/area,_ALL_/status,_ALL_/page,1/pernum,200/']
    def parse(self, response):
        if re.match('^(http|https|ftp)\://list.pad.kankan.com/common_mobile_list/.*',response.url): 
            jsonObj = json.loads(response.body_as_unicode())  
            if jsonObj['data']['pageIndex'] == 1:
                page_count = jsonObj['data']['totalPages'] 
                for page in range(2,page_count+1):
                    url = re.sub('/page,1/','/page,%d/'%page,response.url)
                    yield scrapy.Request(url,dont_filter = False) 
            show_ids = []
            for item in jsonObj['data']['items']:
                yield scrapy.Request('http://api.pad.kankan.com/api.php?movieid=%s&type=movie&mod=detail'%item['id'],callback = self.detail_parse,priority=1, dont_filter = False)
        else:
            #http://data.movie.kankan.com/movie/91473
            aid = re.search('data.movie.kankan.com/movie/(\d+)',response.url).group(1)
            yield scrapy.Request('http://api.pad.kankan.com/api.php?movieid=%s&type=movie&mod=detail'%aid,callback = self.detail_parse,priority=1, dont_filter = False)
    def detail_parse(self,response):
        item = json.loads(response.body_as_unicode())   
        tvplay = TVPlayItem()
        tvplay["website"] = 'kankan'
        tvplay["url"] = 'http://data.movie.kankan.com/movie/%s'%item['id']
        tvplay["aid"] = item['id']
        tvplay["name"] = item['title']
        tvplay["area"] = item['area']
        tvplay["desc"] = item['intro']
        tvplay["alias"] = item['en_title']
        tvplay["episodes"] = item['totalEpisodeCount']
        tvplay["directors"] = ','.join(item['directors'])
        tvplay["actors"] = ','.join(item['actors']) 
        tvplay["cover_img_sm"] = item['poster']
        tvplay["cover_img"] = item['poster'] 
        tvplay["playdate" ] =  str(datetime.today())
        tvplay["playCount" ] =  int(item['play_times'].replace(',',''))
        try:
            tvplay["tags" ] =   ','.join(item['tags']) if item['tags'] else None
        except:
            tvplay["tags"] = ""
        tvplay["lastepisode"] = item['episodeCount']
        yield tvplay