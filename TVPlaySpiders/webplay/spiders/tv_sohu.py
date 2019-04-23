# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import json
import re
from webplay.items import TVPlayItem

class SohuSpider(scrapy.Spider):
    name = "tv_sohu"
       
    
    start_urls = ['https://tv.sohu.com/s2018/dsjphgl/','http://api.tv.sohu.com/v4/search/channel/sub.json?subId=187&page_size=50&offset=0&api_key=f351515304020cad28c92f70f002261c&plat=17&sver=1.0&partner=1','http://tv.sohu.com/frag/vrs_inc/phb_tv_day_100.js']

    def parse(self, response):
        if re.match('^(http|https|ftp)\://tv.sohu.com/frag/vrs_inc/phb_tv_day_100.js',response.url):
            ranklist = re.search('var phb_tv_day_100=({.*});',response.body_as_unicode()).group(1) 
            rankTVlist = json.loads(ranklist)
            for item in rankTVlist['videos']:
                tvplay = TVPlayItem()
                #"url":'http://m.tv.sohu.com/v%s.shtml' %item['aid'],
                #"alias":item['albumDocInfo']['albumEnglishTitle'] 
                tvplay['website'] = 'sohu'
                tvplay["area"] = item['area']
                tvplay["aid"] = item['sid']
                tvplay["directors"] = item['DIRECTOR'] if 'DIRECTOR' in item else ''
                tvplay["actors"] = item['MAIN_ACTOR']  if 'MAIN_ACTOR' in item else ''
                tvplay["episodes"] = item['tv_set_total']
                #tvplay["playStatus"] = item['tip']
                tvplay["releaseDate"] = item['issue_time']
                tvplay["genre"] = ','.join(item['tv_cont_cats'])
                #"tag"] = item['albumDocInfo']['albumTitle']
                tvplay["desc"] = item['tv_desc']
                tvplay["name"] = item['tv_name']             
                #tvplay["playCount"] = item['play_count']
                tvplay["cover_img_sm"] = item["tv_small_pic"]
                tvplay["cover_img"] = item["tvVerBigPic"] if 'tvVerBigPic' in item else None
                tvplay["playdate" ] =  str(datetime.today())
                tvplay["lastepisode"] = item['tv_set_now']
                #"videoType"] = item['albumDocInfo']['channel'] 
                
                #album['tvplayid']= md5(album['url'])
                request = scrapy.Request('http://count.vrs.sohu.com/count/query_Album.action?albumId=%s&type=2' %tvplay['aid'],callback = self.stats_parse,priority=1, dont_filter = False)
                request.meta['tvplay'] = tvplay
                yield request 
        elif re.match('^(http|https|ftp)\://api.tv.sohu.com/v4/search/channel/sub.json.*',response.url): 
            jsonObj = json.loads(response.body_as_unicode()) 
            if re.search('offset=0&',response.url):
                total_num = jsonObj['data']['count']
                page_size = int(re.search('page_size=(\d+)',response.url).group(1))
                total_page = total_num/page_size if total_num%page_size == 0 else int(total_num/page_size) + 1   
                for page in range(1,total_page):
                    url = re.sub('offset=0&','offset=%d&' % (page*page_size) ,response.url)
                    yield scrapy.Request(url,dont_filter = False)
                    
            for item in jsonObj['data']['videos']: 
                tvplay = TVPlayItem()
                #"url":'http://m.tv.sohu.com/v%s.shtml' %item['aid'],
                #"alias":item['albumDocInfo']['albumEnglishTitle'] 
                tvplay['website'] = 'sohu'
                tvplay["area"] = item['area']
                tvplay["aid"] = item['aid']
                tvplay["directors"] = item['director'] if 'director' in item else ''
                tvplay["actors"] = item['main_actor'] if 'main_actor' in item else ''
                tvplay["episodes"] = item['total_video_count']
                tvplay["playStatus"] = item['tip']
                tvplay["releaseDate"] = item['publish_time'] if 'publish_time' in item else ''
                tvplay["genre"] = item['second_cate_name']
                #"tag"] = item['albumDocInfo']['albumTitle']
                tvplay["desc"] = item['album_desc']
                tvplay["name"] = item['album_name']             
                tvplay["playCount"] = item['play_count']
                tvplay["cover_img_sm"] = item["ver_high_pic"]
                tvplay["cover_img"] = item["ver_w12_pic"] if 'ver_w12_pic' in item else None
                tvplay["playdate" ] =  str(datetime.today())
                tvplay["lastepisode"] = item['latest_video_count']
                #"videoType"] = item['albumDocInfo']['channel'] 
            
                #album['tvplayid']= md5(album['url'])
                request = scrapy.Request('http://search.vrs.tv.sohu.com/sv?aid=%s' %tvplay['aid'],callback = self.tvplayurl_parse,priority=1, dont_filter = False)
                request.meta['item'] = tvplay
                yield request
        else:
            tvplay = TVPlayItem()
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
        if 'url' not in tvplay:
            request = scrapy.Request('http://search.vrs.tv.sohu.com/sv?aid=%s' %tvplay['aid'],callback = self.tvplayurl_parse,priority=1, dont_filter = False)
            request.meta['item'] = tvplay
            yield request
        else:
            yield tvplay
            
    def tvplayurl_parse(self,response):
        json_obj = re.search('var =({.+})',response.body_as_unicode()).group(1)
        tvplayurl = json.loads(json_obj)
        tvplay = response.meta['item']
        tvplay['url'] = tvplayurl['lang'][0]['url'] 
        return tvplay