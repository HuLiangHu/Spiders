# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import json
import re
from random import choice 
from variety.items import VarietyItem,VarietyVideoItem

#http://api.mobile.youku.com/layout/android5_0/play/detail?pid=bb2388e929bc3038&guid=8cf328de53f363c2be6b43a5cb2511c2&format=&id=0a007a10e9c211e5b522&area_code=1
class YoukuSpider(scrapy.Spider):
    name = "variety_youku" 
    
    CLIENT_IDS = ['601a5d6a43a8b0f4' ,'d68017cf81224349' ,'70ecad56b9804e77']
    MAX_COUNT = 1500
    cookies = {'sec' :'58aba876b30e38f721c189435e44dcac996ae2c3', 'ykss' :'76a8ab58cc822bdaebb219fe'}
    custom_settings = {
        "DOWNLOAD_DELAY" : 0.5
    }
    def __init__(self):
        super(YoukuSpider ,self).__init__()
        genres = ['']
        for genre in genres:
            self.start_urls.append \
                ( 'https://openapi.youku.com/v2/shows/by_category.json?client_id=%s&category=综艺&orderby=updated&count=20&page=1&genre=%s' %
                (choice(self.CLIENT_IDS) ,genre))

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, cookies=self.cookies)

    def parse(self, response):
        if re.match('^(http|https|ftp)\:\/\/openapi.youku.com\/v2\/shows\/by_category.json.*' ,response.url):
            jsonObj = json.loads(response.body_as_unicode())
            if re.search('page=1&' ,response.url):
                page_size = int(re.search('count=(\d+)' ,response.url).group(1))
                total_count = int(jsonObj['total']) if int(jsonObj['total'] ) <self.MAX_COUNT else self.MAX_COUNT
                page_count = total_count/ page_size if total_count % page_size == 0 else total_count / page_size + 1
                for page in range(2, page_count + 1):
                    url = re.sub('page=1&', 'page=%d&' % page, response.url)
                    yield scrapy.Request(url, dont_filter=False)
            show_ids = []

            for item in jsonObj['shows']:
                tvplay = VarietyItem()
                tvplay["website"] = 'youku'
                tvplay["url"] = 'http://www.youku.com/show_page/id_z%s.html' %item['id']
                
                tvplay["cover_img"] = item['poster'] 
                tvplay["area"] = ''
                tvplay["aid"] = item['id'] 
                tvplay["playStatus"] = ''
                
                tvplay["category"] = item['category']
                #"tag"] = item['albumDocInfo']['albumTitle'],
                tvplay["desc"] =''
                tvplay["name"] = item['name']           
                tvplay["playCount"] = item['view_count'].replace(',','')
              
                tvplay["playdate" ] =  str(datetime.today()) 
                yield tvplay
    def detail_parse(self,response):
        jsonObj = json.loads(response.body_as_unicode()) 
        
        item = jsonObj['detail']
        
        tvplay = VarietyItem()
        tvplay["website"] = 'youku'
        tvplay["url"] = 'http://www.youku.com/show_page/id_z%s.html' %item['showid']
        
        tvplay["cover_img"] = item['img'] 
        tvplay["area"] = ','.join(item['area'])
        tvplay["aid"] = item['showid'] 
        tvplay["playStatus"] = item['stripe_bottom']
        
        tvplay["category"] = item['cats']
        #"tag"] = item['albumDocInfo']['albumTitle'],
        tvplay["desc"] = item['desc']
        tvplay["name"] = item['title']           
        tvplay["playCount"] = item['total_vv'].replace(',','')
        #"videoType"] = item['category']
        tvplay["additional_infos"] = {"total_comment":item['total_comment'],
        "total_down":item['total_down'],"total_up":item['total_up'],
        "total_fav":item['total_fav']} 
        tvplay["playdate" ] =  str(datetime.today()) 
        tvplay["tv" ] =  ','.join(item['station'])
        yield tvplay
        
        #yield scrapy.Request('http://api.mobile.youku.com/shows/%s/reverse/videos?pid=bb2388e929bc3038&guid=8cf328de53f363c2be6b43a5cb2511c2&pg=1&pz=50&area_code=1' %tvplay['aid'],\
        #meta = {'albumurl':tvplay['url'],'aid':tvplay['aid']},callback = self.videos_parse,priority=1, dont_filter = True)
        
    def videos_parse(self,response):
        albumurl = response.meta['albumurl']
        aid = response.meta['aid']
        jsonObj = json.loads(response.body_as_unicode())  
        if re.search('pg=1&',response.url):
            page_size = int(jsonObj['pz'])
            total_count = int(jsonObj['total'])
            page_count = total_count/page_size if total_count%page_size == 0 else total_count/page_size +1
            for page in range(2,page_count+1):
                url = re.sub('pg=1&','pg=%d&'%page,response.url)
                yield scrapy.Request(url,meta = {'albumurl':albumurl,'aid':aid},callback = self.videos_parse,priority=1)
        for item in jsonObj['results']:
            video = VarietyVideoItem()
            video['url'] = 'http://v.youku.com/v_show/id_%s.html' %item['videoid']
            video['aid'] = aid
            video['vid'] = item['videoid']
            video["website"] = 'youku'
            video['albumurl'] = albumurl
            video["playdate" ] =  str(datetime.today()) 
            video["playCount" ] =  item['total_pv']
            video["video_img" ] =  item['img_hd']
            video["name" ] =  item['title']
            video["desc" ] =  item['desc']
            video["releaseDate" ] =  item['stg']
            video["episode" ] =  item['stg']
            video["additional_infos"] = {"total_comment":item['total_comment'],
            "total_down":item['total_down'],"total_up":item['total_up'],
            "total_fav":item['total_fav']} 
            yield video