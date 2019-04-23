# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import json
import re
from webplay.items import MovieItem
import logging

class IQiyiSpider(scrapy.Spider):
    name = "movie_iqiyi"
    start_urls = ['http://search.video.qiyi.com/o?pageNum=1&mode=11&ctgName=电影&threeCategory=&pageSize=50&type=list&if=html5&pos=1&site=iqiyi&access_play_control_platform=15']
    
    def __init__(self):
        super(IQiyiSpider,self).__init__()
        categories = ['喜剧','悲剧','爱情','动作','枪战','犯罪','惊悚','恐怖','悬疑','动画','家庭','奇幻','魔幻','科幻','战争','青春']    
         
        for category in categories:
            self.start_urls.append('http://search.video.qiyi.com/o?pageNum=1&mode=11&ctgName=电影&threeCategory=%s&pageSize=50&type=list&if=html5&pos=1&site=iqiyi&access_play_control_platform=15'%category)
    
    def parse(self, response):
        if re.match('^(http|https|ftp)\://search.video.qiyi.com/.*',response.url): 
            result = json.loads(response.body_as_unicode())
            if re.search('pageNum=1&',response.url) and result: 
                page_size = int(re.search('pageSize=(\d+)',response.url).group(1))
                total_num = result['data']['result_num']
                total_page = total_num/page_size if total_num % page_size == 0 else int(total_num/page_size) + 1
                for page in range(2,total_page +1):
                    url = re.sub('pageNum=1&','pageNum=%d&' %page,response.url)
                    yield scrapy.Request(url,callback = self.parse)
            
            for item in result['data']['docinfos']: 
                if 'albumLink' in item['albumDocInfo']:
                    tvplay = MovieItem()
                    tvplay["url"] = item['albumDocInfo']['albumLink']
                    tvplay["website"] = 'iqiyi'
                    #"ename":item['albumDocInfo']['albumEnglishTitle'],
                    #tvplay["score"] = item['albumDocInfo']['score']
                    tvplay["area"] = item['albumDocInfo']['region']
                    tvplay["aid"] = item['albumDocInfo']['albumId']
                    tvplay["playdate"] =  str(datetime.today())
                    tvplay["directors"] = item['albumDocInfo']['director'] if 'director' in item['albumDocInfo'] else ''
                    tvplay["actors"] = item['albumDocInfo']['star'] if 'star' in item['albumDocInfo'] else ''
                     
                    tvplay["playStatus"] = item['albumDocInfo']['playTime'] if 'playTime' in item['albumDocInfo'] else ''
                    tvplay["releaseDate"] = item['albumDocInfo']['releaseDate']
                    tvplay["genre"] = ','.join(item['albumDocInfo']['video_lib_meta']['category']) if 'category' in item['albumDocInfo']['video_lib_meta']   else ''
                    tvplay["tags"] = re.sub(',\d+','',item['albumDocInfo']['threeCategory']).replace(' ',',')
                    tvplay["desc"] = item['albumDocInfo']['video_lib_meta']['description'] if 'description' in item['albumDocInfo']['video_lib_meta'] else ''
                    tvplay["name"] = item['albumDocInfo']['albumTitle']           
                    #tvplay["playCount"] = item['albumDocInfo']['playCount']
                    tvplay["cover_img_sm"] = item['albumDocInfo']['albumHImage']
                    tvplay["cover_img"] = item['albumDocInfo']['video_lib_meta']['poster'] if 'poster' in item['albumDocInfo']['video_lib_meta'] else None
                    request = scrapy.Request('http://cache.video.qiyi.com/jp/pc/%s/'%tvplay["aid"],callback = self.stats_parse)
                    request.meta['tvplay'] = tvplay
                    yield request
        else:
            tvplay = MovieItem()
            aid = re.search('albumId: (\d+),',response.body_as_unicode()).group(1)
            tvplay["website"] = 'iqiyi'
            tvplay['aid'] = aid
            tvplay['url'] = response.url
            name = re.search('<meta name="keywords" content="(.+)" />',response.body_as_unicode()).group(1)
            tvplay['name'] = name
            tvplay["playdate"] =  str(datetime.today())
            request = scrapy.Request('http://cache.video.qiyi.com/jp/pc/%s/'%aid,callback = self.stats_parse)
            request.meta['tvplay'] = tvplay
            yield request
            
    def stats_parse(self,response):
        tvplay = response.meta['tvplay']
        tvplay['playCount'] = re.search('{"\d+":(\d+)}',response.body_as_unicode()).group(1)
        yield tvplay
        '''
        request = scrapy.Request('http://api-t.iqiyi.com/qx_api/comment/get_video_comments?categoryid=1&need_total=1&page=1&page_size=1&sort=hot&tvid=%s'%tvplay['aid'],callback = self.commentcount_parse)
        request.meta['tvplay'] = tvplay
        yield request
        '''
    def commentcount_parse(self,response):
        tvplay = response.meta['tvplay'] 
        tvplay['commentcount'] = int(re.search('"count":(\d+)',response.body_as_unicode()).group(1))
        yield tvplay
           