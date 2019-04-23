# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import json
import re
from variety.items import VarietyItem,VarietyVideoItem

class LetvSpider(scrapy.Spider):
    name = "variety_letv"
    start_urls = ( 
        'http://list.le.com/getLesoData?from=pc&src=1&stype=1&ps=30&pn=1&ph=420001&dt=1&cg=11&or=4&stt=1&s=3',
    )

    def parse(self, response):
        if re.match('^(http|https|ftp)\://list.le.com/.*',response.url): 
            listObj  = json.loads(response.body_as_unicode()) 
            # if re.search('&p=1&',response.url):
            #     total_size = listObj['album_count']
            #     total_page = total_size / 30 if total_size%30 == 0 else total_size/30 +1
            #     for i in range(2,int(total_page) +1 ):
            #         next_page = re.sub('p=1','p=%s'%i,response.url)
            #         yield scrapy.Request(next_page,dont_filter = False)
            if len(listObj['data']['arr'])>0:
                page = int(re.search('&pn=(\d+)&',response.url).group(1))
                if page < 50: #防止无限制循环
                    next_page = re.sub('&pn=\d+&','&pn=%s&'%(page+1),response.url)
                    yield scrapy.Request(next_page)

            for item in listObj['data']['arr']:
                try:
                    players = [item['starring'][str(attr)] for attr in item['starring']] 
                except:
                    players = []
                tvplay = VarietyItem()
                tvplay["area"] = item['areaName']
                tvplay["url"] = "http://www.le.com/zongyi/%s.html"%item['aid'] 
                tvplay["aid"] = item['aid']
                tvplay["name"] = item['name']
                tvplay["desc"] = item['description']
                tvplay["player"] = ','.join(players) 
                tvplay["category"] = item['subCategoryName']
                tvplay["playStatus"] = item['playStatus']
                tvplay["releaseDate"] = item['releaseDate'] 
                tvplay["tags"] = item['tag']
                #tvplay["tv"] = item['tvName']
                              
                tvplay["playCount"] = item['playCount'] 
                tvplay["lastseries"] = item['nowEpisodes']
                tvplay["playdate"] = str(datetime.today())
                tvplay["website"] = 'letv'
                tvplay["playCount"] = item['playCount'] 
                #request = scrapy.Request('http://v.stat.le.com/vplay/queryMmsTotalPCount?cid=2&mid=0&pid=%s'%tvplay['aid'],callback = self.stats_parse)
                #request.meta['tvplay'] = tvplay
                yield tvplay
                
                #视频专辑
                #http://api.le.com/mms/out/album/videos?id=52244&cid=11&platform=pc&vid=25019174&relvideo=0&relalbum=0&page=2
                request = scrapy.Request('http://api.le.com/mms/out/album/videos?id=%s&cid=11&platform=pc&relvideo=0&page=1&relalbum=0' % (item['aid']),callback = self.videos_parse)
                #yield request
        else:
            tvplay = VarietyItem()
            tvplay["url"] = response.url
            tvplay['aid'] = re.search('pid: "(\d+)"',response.body_as_unicode()).group(1)
            tvplay['name'] = re.search('title: "(.+)"',response.body_as_unicode()).group(1)
            tvplay["playdate"] = str(datetime.today())
            tvplay["website"] = 'letv'
            request = scrapy.Request('http://v.stat.le.com/vplay/queryMmsTotalPCount?cid=2&mid=0&pid=%s'%tvplay['aid'],callback = self.stats_parse)
            request.meta['tvplay'] = tvplay
            yield request
    
    def videos_parse(self,response):
        listObj  = json.loads(response.body_as_unicode())
        total_size = listObj['total']
        aid = re.search('id=(\d+)',response.url).group(1)
        if re.search('&page=1',response.url):
            total_page = total_size / 100 if total_size%100 == 0 else total_size/100 +1
            for i in range(2,total_page +1 ): 
                yield scrapy.Request('http://api.le.com/mms/out/album/videos?id=%s&cid=11&platform=pc&relvideo=0&page=%s&relalbum=0' %(aid,i),callback = self.videos_parse)
        for item in listObj['data']:
            video = VarietyVideoItem() 
            
            video['url'] = 'http://www.le.com/ptv/vplay/%s.html' %item['vid']
            video['aid'] = aid
            video['vid'] = item['vid']
            video['albumurl'] = "http://www.le.com/zongyi/%s.html" % aid 
            video['video_img'] = item['pic']
            video['name'] = item['title']
            video['desc'] = item['subTitle']
            video['player'] = item['guest']
            video['releaseDate'] = item['releaseDate']
            video["website"] = 'letv'
            video['duration'] = item['duration']
            video['episode'] = item['episode']
            video["playdate"] = str(datetime.today())
            #http://v.stat.letv.com/vplay/queryMmsTotalPCount?pid=52244&cid=11&vid=2111152
            request = scrapy.Request('http://v.stat.letv.com/vplay/queryMmsTotalPCount?pid=%s&cid=11&vid=%s'%(aid,item['vid']),callback = self.stats_parse)
            request.meta['tvplay'] = video
            yield request
            
    def stats_parse(self,response):
        tvplay = response.meta['tvplay']
        statsinfo = json.loads(response.body_as_unicode())
        tvplay['playCount'] = statsinfo['plist_play_count']
        tvplay["playdate"] = str(datetime.today())
        yield tvplay