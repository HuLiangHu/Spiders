# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import json
import re
from webplay.items import MovieItem
import logging
class LetvSpider(scrapy.Spider):
    name = "movie_letv"
    start_urls = ['http://list.le.com/getLesoData?from=pc&src=1&stype=1&ps=30&pn=2&ph=420001&dt=1&cg=1&or=4&stt=1&vt=180001&s=1']

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
                tvplay = MovieItem()
                tvplay["area"] = item['areaName']
                tvplay["url"] = item["urlLink"]
                tvplay["aid"] = item['aid']
                tvplay["directors"] = ','.join(directory)
                tvplay["actors"] = ','.join(actors)
                tvplay["playStatus"] = item['playStatus']
                tvplay["releaseDate"] = item['releaseDate']
                tvplay["genre"] = item['subCategoryName']
                tvplay["tags"] = item['tag']
                tvplay["desc"] = item['description']
                tvplay["name"] = item['name']              
                tvplay["playCount"] = item['playCount'] 
                tvplay["playdate"] = str(datetime.today())
                tvplay["website"] = 'letv'
                yield tvplay