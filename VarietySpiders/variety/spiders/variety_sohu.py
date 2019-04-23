# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import json
import re
from variety.items import VarietyItem,VarietyVideoItem

class SohuSpider(scrapy.Spider):
    name = "variety_sohu" 
    start_urls = (
       'http://api.tv.sohu.com/v4/search/channel.json?sub_channel_id=1060000&cid=7&offset=0&cursor=0&page_size=50&api_key=f351515304020cad28c92f70f002261c',
    )

    def parse(self, response):
        if re.match('^(http|https|ftp)\://api.tv.sohu.com/v4/search/channel.json.*',response.url): 
            jsonObj = json.loads(response.body_as_unicode()) 
            if re.search('offset=0&',response.url):
                total_num = jsonObj['data']['count']
                page_size = int(re.search('page_size=(\d+)',response.url).group(1))
                total_page = total_num/page_size if total_num%page_size == 0 else int(total_num/page_size) + 1   
                for page in range(1,total_page):
                    url = re.sub('offset=0&','offset=%d&' % (page*page_size) ,response.url)
                    yield scrapy.Request(url)
                    
            for item in jsonObj['data']['videos']: 
                tvplay = VarietyItem()
                #"url":'http://m.tv.sohu.com/v%s.shtml' %item['aid'],
                #"alias":item['albumDocInfo']['albumEnglishTitle'] 
                tvplay['website'] = 'sohu'
                tvplay['url'] = 'http://m.tv.sohu.com/v%s.shtml' %item['aid']
                tvplay["area"] = item['area']
                tvplay["aid"] = item['aid']  
                tvplay["category"] = item['second_cate_name']
                #"tag"] = item['albumDocInfo']['albumTitle']
                tvplay["desc"] = item['album_desc']
                tvplay["name"] = item['album_name']             
                #tvplay["playCount"] = item['play_count'] 
                tvplay["cover_img"] = item["ver_w12_pic"] if 'ver_w12_pic' in item else None
                tvplay["playdate" ] =  str(datetime.today())
                tvplay["lastseries"] = item['latest_video_count']
                #"videoType"] = item['albumDocInfo']['channel'] 
                request = scrapy.Request('http://count.vrs.sohu.com/count/query_album.action?albumId=%s&type=2'%tvplay['aid'],callback = self.stats_parse)
                request.meta['tvplay'] = tvplay
                yield request
                #album['tvplayid']= md5(album['url'])
                request = scrapy.Request('http://pl.hd.sohu.com/videolist?playlistid=%s&pagenum=1&pagesize=100&order=1' %tvplay['aid'],callback = self.videos_parse,priority = 1)
                #request = scrapy.Request('http://search.vrs.tv.sohu.com/sv?aid=%s' %tvplay['aid'],callback = self.tvplayurl_parse,priority=1, dont_filter = True)
                request.meta['item'] = tvplay
                #yield request
        else:
            tvplay = VarietyItem()
            tvplay['website'] = 'sohu'
            tvplay['name'] = re.search('<h1 class="color3"><a href=\'http://tv.sohu.com/drama/\'>.+</a>.(.+) </h1>',response.body_as_unicode()).group(1)
            tvplay['url'] = response.url
            tvplay['aid'] = re.search('var PLAYLIST_ID="(\d+)";',response.body_as_unicode()).group(1)
            #request = scrapy.Request('http://count.vrs.sohu.com/count/query_album.action?albumId=%s&type=2'%tvplay['aid'],callback = self.stats_parse,dont_filter = True)
            request = scrapy.Request('http://count.vrs.sohu.com/count/queryext.action?pids=%s'%tvplay['aid'],callback = self.stats_parse)
            request.meta['tvplay'] = tvplay
            yield request
            
            request = scrapy.Request('http://pl.hd.sohu.com/videolist?playlistid=%s&pagenum=1&pagesize=100&order=1' %tvplay['aid'],callback = self.videos_parse,priority = 1)
            #request = scrapy.Request('http://search.vrs.tv.sohu.com/sv?aid=%s' %tvplay['aid'],callback = self.tvplayurl_parse,priority=1, dont_filter = True)
            request.meta['item'] = tvplay
            #yield request
            
    
    def videos_parse(self,response):
       
        jsonObj = json.loads(response.body_as_unicode()) 
        if re.search('pagenum=1&',response.url) and jsonObj: 
            show = response.meta['item']
            page_size = int(re.search('pagesize=(\d+)',response.url).group(1))
            total_num = jsonObj['size']
            total_page = total_num/page_size if total_num % page_size == 0 else int(total_num/page_size) + 1 
            for page in range(2,total_page +1):
                url = re.sub('pagenum=1&','pagenum=%d&' %page,response.url)
                yield scrapy.Request(url,callback = self.videos_parse)
            
            show['url'] = jsonObj['albumPageUrl']
            show['tv'] = jsonObj['copyright']
            yield show
        for item in jsonObj['videos']:
            video = VarietyVideoItem()
            video['url'] = item['pageUrl']
            video['aid'] = jsonObj['playlistid']
            video['vid'] = item['tvId']
            video['albumurl'] = jsonObj['albumPageUrl']
            video['playdate'] = str(datetime.today())
            video['playCount'] = item['pageUrl']
            video['video_img'] = item['largePicUrl']
            video['name'] = item['name']
            video['desc'] = item['videoDesc']
            video['player'] = ','.join([d['starName'] for d in item['divGMap']])
            video['releaseDate'] = item['publishTime']
            video['website'] = 'sohu'
            video['duration'] = item['playLength']
            video['episode'] = item['showDate']
            #http://count.vrs.sohu.com/count/queryext.action?vids=2961872&plids=9107368
            
            yield scrapy.Request('http://count.vrs.sohu.com/count/queryext.action?vids=%s'%video['vid'],meta={'tvplay':video},callback = self.stats_parse,priority = 2)
    
    def stats_parse(self,response):
        tvplay = response.meta['tvplay']
        tvplay["playdate" ] =  str(datetime.today())
        tvplay['playCount'] = int(re.search('count=(\d+)',response.body_as_unicode()).group(1))
        
        request = scrapy.Request('http://search.vrs.tv.sohu.com/sv?aid=%s' %tvplay['aid'],callback = self.tvplayurl_parse,priority=1)
        request.meta['item'] = tvplay
        yield request
        
        #yield tvplay
            
    def tvplayurl_parse(self,response):
        json_obj = re.search('var =({.+})',response.body_as_unicode()).group(1)
        tvplayurl = json.loads(json_obj)
        tvplay = response.meta['item']
        tvplay['url'] = tvplayurl['lang'][0]['url'] 
        return tvplay