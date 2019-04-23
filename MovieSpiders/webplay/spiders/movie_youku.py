# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import json
import re
from random import choice 
from webplay.items import MovieItem
import logging
#http://api.mobile.youku.com/layout/android5_0/play/detail?pid=bb2388e929bc3038&guid=8cf328de53f363c2be6b43a5cb2511c2&format=&id=0a007a10e9c211e5b522&area_code=1
class YoukuSpider(scrapy.Spider):
    name = "movie_youku" 
    start_urls = []
    CLIENT_IDS = ['601a5d6a43a8b0f4','d68017cf81224349','70ecad56b9804e77']
    cookies = {'sec':'58aba876b30e38f721c189435e44dcac996ae2c3', 'ykss':'76a8ab58cc822bdaebb219fe'}
    MAX_COUNT = 1500
    custom_settings = {
        "DOWNLOAD_DELAY" : 1
    }
    def __init__(self):
        super(YoukuSpider,self).__init__()
        genres = ['武侠','警匪','犯罪','科幻','战争','恐怖','惊悚','纪录片','西部','戏曲','歌舞','奇幻','冒险','悬疑','历史','动作','传记','动画','儿童','喜剧','爱情','剧情','运动','短片','优酷出品']
        for genre in genres:
            self.start_urls.append('https://openapi.youku.com/v2/shows/by_category.json?client_id=%s&category=电影&count=20&page=1&genre=%s'%(choice(self.CLIENT_IDS),genre)) 
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, cookies=self.cookies) 
    def parse(self, response):
        if re.match('^(http|https|ftp)\://openapi.youku.com/v2/shows/by_category.json.*',response.url): 
            jsonObj = json.loads(response.body_as_unicode())  
            if re.search('page=1&',response.url):
                page_size = int(re.search('count=(\d+)',response.url).group(1))
                total_count = int(jsonObj['total']) if int(jsonObj['total'])<self.MAX_COUNT else self.MAX_COUNT 
                page_count = int(total_count/page_size if total_count%page_size == 0 else total_count/page_size +1)
                for page in range(2,page_count+1):
                    url = re.sub('page=1&','page=%d&'%page,response.url)
                    yield scrapy.Request(url,dont_filter = False) 
            show_ids = []
            
            for item in jsonObj['shows']:  
                show_ids.append(item['id']) 
            if len(show_ids)>0: 
                yield scrapy.Request('https://openapi.youku.com/v2/shows/show_batch.json?client_id=%s&show_ids=%s'%(choice(self.CLIENT_IDS),','.join(show_ids)),callback = self.detail_parse,priority=1, dont_filter = False)
        else:
            aid = re.search('id_\w(\w+).html',response.url).group(1)
            yield scrapy.Request('https://openapi.youku.com/v2/shows/show_batch.json?client_id=%s&show_ids=%s'%(choice(self.CLIENT_IDS),aid),callback = self.detail_parse,priority=2, dont_filter = False) 
    def detail_parse(self,response):
        jsonObj = json.loads(response.body_as_unicode()) 
        
        for item in jsonObj['shows']:  
            director = ''
            actors = ''   
            if item['attr']['director']:
                director = ','.join([pers['name'] for pers in item['attr']['director']])
            if item['attr']['performer']:
                actors = ','.join([pers['name'] for pers in item['attr']['performer']]) 
            tvplay = MovieItem()
            tvplay["website"] = 'youku'
            tvplay["url"] = item['link']
            tvplay["alias"] = item['subtitle']
            tvplay["cover_img_sm"] = item['poster']
            tvplay["cover_img"] = item['poster_large'] 
            tvplay["area"] = item['area']
            tvplay["aid"] = item['id']
            tvplay["directors"] = director
            tvplay["actors"] = actors
            tvplay["playStatus"] = item['update_notice']
            tvplay["releaseDate"] = item['published']#youku上线时间
            #tvplay["releaseDate"] = item['released'], #节目发行时间
            tvplay["genre"] = item['genre']
            #"tag"] = item['albumDocInfo']['albumTitle'],
            tvplay["desc"] = item['description']
            tvplay["name"] = item['name']           
            tvplay["playCount"] = item['view_count']
            #"videoType"] = item['category']
            tvplay["additional_infos"] = {"up_count":item['up_count'],
            "down_count":item['down_count'],"favorite_count":item['favorite_count'],
            "douban_num":item['douban_num'],"comment_count":item['comment_count']} 
            tvplay['commentcount'] = item['comment_count']
            tvplay["playdate" ] =  str(datetime.today())
            
            yield tvplay