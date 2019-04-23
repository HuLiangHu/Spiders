# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import json
import re
from variety.items import VarietyItem,VarietyVideoItem

class IQiyiSpider(scrapy.Spider):
    name = "variety_iqiyi"
    start_urls = ( 'http://search.video.qiyi.com/o?pageNum=1&mode=11&ctgName=综艺&threeCategory=&pageSize=50&type=list&if=html5&pos=1&site=iqiyi&access_play_control_platform=15',
    )
    
    def parse(self, response):
        if re.match('^(http|https|ftp)\://search.video.qiyi.com/.*',response.url): 
            result = json.loads(response.body_as_unicode())
            if re.search('pageNum=1&',response.url) and result: 
                page_size = int(re.search('pageSize=(\d+)',response.url).group(1))
                total_num = result['data']['result_num'] if  result['data']['result_num'] else 1000
                total_page = total_num/page_size if total_num % page_size == 0 else int(total_num/page_size) + 1 
                for page in range(2,total_page +1):
                    url = re.sub('pageNum=1&','pageNum=%d&' %page,response.url)
                    yield scrapy.Request(url,callback = self.parse)

            for item in result['data']['docinfos']: 
                if 'albumLink' in item['albumDocInfo']:
                    tvplay = VarietyItem()
                    tvplay["url"] = item['albumDocInfo']['albumLink']
                    tvplay["website"] = 'iqiyi' 
                    tvplay["area"] = item['albumDocInfo']['region']
                    tvplay["aid"] = item['albumDocInfo']['albumId']
                    tvplay["playdate"] =  str(datetime.today())
                    tvplay["host"] = item['albumDocInfo']['star'] if 'star' in item['albumDocInfo'] else '' 
                    tvplay["releaseDate"] = item['albumDocInfo']['releaseDate']
                    tvplay["category"] = ','.join(item['albumDocInfo']['video_lib_meta']['category']) if 'category' in item['albumDocInfo']['video_lib_meta']   else ''
                    tvplay["tags"] = re.sub(',\d+','',item['albumDocInfo']['threeCategory']).replace(' ',',')
                    tvplay["desc"] = item['albumDocInfo']['video_lib_meta']['description'] if 'description' in item['albumDocInfo']['video_lib_meta'] else ''
                    tvplay["name"] = item['albumDocInfo']['albumTitle']    
                    
                    tvplay["cover_img"] = item['albumDocInfo']['video_lib_meta']['poster'] if 'poster' in item['albumDocInfo']['video_lib_meta'] else None
                    tvplay['lastseries'] = item['albumDocInfo']['videoinfos'][0]['year']
                    request = scrapy.Request('http://cache.video.qiyi.com/jp/pc/%s/'%tvplay["aid"],callback = self.stats_parse)
                    request.meta['tvplay'] = tvplay
                    yield request
                    sourceCode = item['albumDocInfo']['sourceCode']
                    
                    categoryid = re.search('.*,(\d+)',item['albumDocInfo']['channel']).group(1)
                    #categoryid = re.search('channel: ".*,(\d+)",',item['albumDocInfo']['channel']).group(1)
                    #yield scrapy.Request('http://cache.video.qiyi.com/jp/sdvlst/%s/%s/'%(categoryid,sourceCode),priority=1,meta = {'url':tvplay['url']},callback = self.videos_parse)
        else:
            tvplay = VarietyItem()
            aid = re.search('albumId: (\d+),',response.body_as_unicode()).group(1)
            sourceCode = re.search('sourceId: (\d+),',response.body_as_unicode()).group(1)
            categoryid = re.search('cid:(\d+),',response.body_as_unicode()).group(1)
            tvplay["website"] = 'iqiyi'
            tvplay['aid'] = aid
            tvplay['url'] = response.url
            name = re.search('<meta name="keywords" content="(.+)" />',response.body_as_unicode()).group(1)
            tvplay['name'] = name
            tvplay["playdate"] =  str(datetime.today())
            request = scrapy.Request('http://cache.video.qiyi.com/jp/pc/%s/'%aid,callback = self.stats_parse)
            request.meta['tvplay'] = tvplay
            yield request
            #yield scrapy.Request('http://cache.video.qiyi.com/jp/sdvlst/%s/%s/'%(categoryid,sourceCode),priority=1,meta = {'url':tvplay['url']},callback = self.videos_parse,dont_filter = True)
       
    def videos_parse(self,response):
        content = re.search('var tvInfoJs=(.+)',response.body_as_unicode()).group(1)
        vlist = json.loads(content)
        albumnurl = response.meta['url']
        for item in vlist['data']:
            video = VarietyVideoItem() 
            
            video['url'] = item['vUrl']
            video['aid'] = item['aId']
            video['vid'] = item['tvId']
            video['albumurl'] = albumnurl
            video['video_img'] = item['aPicUrl']
            video['name'] = item['videoName']
            video['desc'] = item['desc'] 
            video['releaseDate'] = item['tvYear']
            video["website"] = 'iqiyi' 
            video['episode'] = item['tvYear']
            video["playdate"] = str(datetime.today())
            video["duration"] = item['timeLength'] 
            #http://v.stat.letv.com/vplay/queryMmsTotalPCount?pid=52244&cid=11&vid=2111152
            request = scrapy.Request('http://cache.video.qiyi.com/jp/pc/%s/'%(item['tvId']),callback = self.stats_parse)
            request.meta['tvplay'] = video
            yield request
            
         
    def stats_parse(self,response):
        tvplay = response.meta['tvplay']
        tvplay['playCount'] = re.search('{"\d+":(\d+)}',response.body_as_unicode()).group(1)
        yield tvplay
           