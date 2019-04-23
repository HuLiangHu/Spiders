# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import json
import re
from webplay.items import TVPlayItem
class LetvSpider(scrapy.Spider):
    name = "tv_letv"
       
    # start_urls = ['http://list.le.com/apin/chandata.json?c=2&d=1&md=&o=20&p=1&s=1']
    start_urls=['http://list.le.com/getLesoData?from=pc&src=1&stype=1&ps=30&pn=1&ph=420001&dt=1&cg=2&or=4&stt=1&vt=180001&s=1','http://list.le.com/getLesoData?from=pc&src=1&stype=1&ps=30&pn=1&ph=420001&dt=1&cg=2&or=5&stt=1&vt=180001&s=1']
                 
    
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
                directory=[]
                for attr in item['directory']:
                    directory.append(attr)
                actors =[]
                for attr in item['starring']:
                    for attr1 in attr:
                        actors.append(attr[attr1])
                tvplay = TVPlayItem()
                tvplay["area"] = item['areaName']
                tvplay["url"] = item["urlLink"].encode("utf8")
                tvplay["aid"] = item['aid']
                tvplay["directors"] = ','.join(directory)
                tvplay["actors"] = ','.join(actors)
                tvplay["episodes"] = item['episodes']
                tvplay["playStatus"] = item['playStatus']
                tvplay["releaseDate"] = item['releaseDate']
                tvplay["genre"] = item['subCategoryName']
                tvplay["tags"] = item['tag']
                tvplay["desc"] = item['description']
                tvplay["name"] = item['name']              
                tvplay["playCount"] = item['playCount'] 
                tvplay["lastepisode"] = item['nowEpisodes']
                tvplay["playdate"] = str(datetime.today())
                tvplay["website"] = 'letv'
                #yield tvplay
                request = scrapy.Request('http://v.stat.le.com/vplay/queryMmsTotalPCount?cid=2&mid=0&pid=%s'%tvplay['aid'],callback = self.stats_parse,dont_filter = False)
                request.meta['tvplay'] = tvplay
                yield request
        # else:
        #     tvplay = TVPlayItem()
        #     tvplay["url"] = response.url
        #     tvplay['aid'] = re.search('pid: "(\d+)"',response.text).group(1)
        #     tvplay['name'] = re.search('title: "(.+)"',response.text).group(1)
        #     tvplay["playdate"] = str(datetime.today())
        #     tvplay["website"] = 'letv'
        #     request = scrapy.Request('http://v.stat.le.com/vplay/queryMmsTotalPCount?cid=2&mid=0&pid=%s'%tvplay['aid'],callback = self.stats_parse,dont_filter = False)
        #     request.meta['tvplay'] = tvplay
        #     yield request
          
    def stats_parse(self,response):
        tvplay = response.meta['tvplay']
        statsinfo = json.loads(response.body_as_unicode())
        tvplay['playCount'] = statsinfo['plist_play_count']
        yield tvplay