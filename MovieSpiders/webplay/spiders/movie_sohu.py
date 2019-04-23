# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import json
import re
from webplay.items import MovieItem
import logging

class SohuSpider(scrapy.Spider):
    name = "movie_sohu" 
    start_urls = [
       'http://api.tv.sohu.com/v4/search/channel.json?sub_channel_id=88880001&cid=8888&cursor=0&page_size=15&api_key=f351515304020cad28c92f70f002261c&plat=17&sver=1.0&&offset=0&partner=1',
      'http://api.tv.sohu.com/v4/search/channel.json?sub_channel_id=1000000&cid=1&cursor=0&page_size=15&api_key=f351515304020cad28c92f70f002261c&plat=17&sver=1.0&&offset=0&partner=1']
    
    
    def parse(self, response):
        if re.match('^(http|https|ftp)\://api.tv.sohu.com/v4/search/channel.json?.*',response.url): 
            jsonObj = json.loads(response.body_as_unicode()) 
            if re.search('offset=0&',response.url):
                total_num = jsonObj['data']['count']
                page_size = int(re.search('page_size=(\d+)',response.url).group(1))
                total_page = total_num/page_size if total_num%page_size == 0 else int(total_num/page_size) + 1   
                for page in range(1,total_page):
                    url = re.sub('offset=0&','offset=%d&' % (page*page_size) ,response.url)
                    yield scrapy.Request(url,dont_filter = False)
                    
            for item in jsonObj['data']['videos']: 
                tvplay = MovieItem()
                #"url":'http://m.tv.sohu.com/v%s.shtml' %item['aid'],
                #"alias":item['albumDocInfo']['albumEnglishTitle'] 
                tvplay['website'] = 'sohu'
                tvplay["area"] = item['area']
                # tvplay["aid"] = item['aid']
                tvplay["aid"] = item['vid']
                tvplay["directors"] = item['director'] if 'director' in item else ''
                tvplay["actors"] = item['main_actor']
                tvplay["playStatus"] = item['tip']
                tvplay["releaseDate"] = item['publish_time']
                tvplay["genre"] = item['second_cate_name'] if 'second_cate_name' in item else ''
                #"tag"] = item['albumDocInfo']['albumTitle']
                tvplay["desc"] = item['album_desc']
                tvplay["name"] = item['album_name']             
                tvplay["playCount"] = item['play_count']
                tvplay["cover_img_sm"] = item["ver_high_pic"] if 'ver_high_pic' in item else None
                tvplay["cover_img"] = item["ver_w12_pic"] if 'ver_w12_pic' in item else None
                tvplay["playdate" ] =  str(datetime.today())
                #"videoType"] = item['albumDocInfo']['channel'] 
            
                #album['tvplayid']= md5(album['url'])
                request = scrapy.Request('http://m.tv.sohu.com/phone_playinfo?callback=jsonpx7&vid=%s&site=1&appid=tv&api_key=f351515304020cad28c92f70f002261c&plat=17&sver=1.0&partner=1' %tvplay['aid'],callback = self.tvplayurl_parse,priority=1, dont_filter = False)
                request.meta['item'] = tvplay
                yield request
        
        else:
            tvplay = MovieItem()
            tvplay['website'] = 'sohu'
            tvplay['name'] = re.search('<h1 class="color3"><a href=\'http://tv.sohu.com/drama/\'>.+</a>.(.+) </h1>',response.body_as_unicode()).group(1)
            tvplay['url'] = response.url
            tvplay['aid'] = re.search('var PLAYLIST_ID="(\d+)";',response.body_as_unicode()).group(1)
            request = scrapy.Request('http://count.vrs.sohu.com/count/query_album.action?albumId=%s&type=2'%tvplay['aid'],callback = self.stats_parse,dont_filter = False)
            request.meta['tvplay'] = tvplay
            yield request
            
    def stats_parse(self,response):
        tvplay = response.meta['tvplay']
        tvplay["playdate" ] =  str(datetime.today())
        tvplay['playCount'] = int(re.search('var count=(\d+);',response.body_as_unicode()).group(1))
        yield tvplay
            
    def tvplayurl_parse(self,response):
        json_obj = re.search('jsonpx7\((.+)\)',response.body_as_unicode()).group(1)
        #json_obj=response.body_as_unicode().replace('jsonpx7(','').replace('});','}')
        tvplayurl=json.loads(json_obj) 
        tvplay = response.meta['item']
        tvplay['url'] = tvplayurl['data']['original_video_url']
        return tvplay