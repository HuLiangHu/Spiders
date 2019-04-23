# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import json
import re
from webplay.items import TVPlayItem
import logging
class IQiyiSpider(scrapy.Spider):
    name = "tv_iqiyi"
    start_urls = [ 
   'http://search.video.iqiyi.com/o?pageNum=1&mode=11&ctgName=%E7%94%B5%E8%A7%86%E5%89%A7&threeCategory=%E5%86%85%E5%9C%B0%3Bmust&content_type=&pageSize=21&type=list&if=html5&pos=1&site=iqiyi&qyid=b1m6wyyzos2knlxe698e1qqb&access_play_control_platform=15&pu=2125035081&u=b1m6wyyzos2knlxe698e1qqb&ispurchase=',
    'http://search.video.iqiyi.com/o?pageNum=1&mode=11&ctgName=电视剧&threeCategory=&pageSize=50&type=list&if=html5&pos=1&site=iqiyi&access_play_control_platform=15']
    def __init__(self):
        super(IQiyiSpider,self).__init__()
        #categories = ['言情剧','历史剧','武侠剧','古装剧','年代剧','农村剧','偶像剧','悬疑剧','科幻剧','喜剧','青春剧','喜剧','宫廷剧','商战剧','神话剧','穿越剧','罪案剧','谍战剧','青春剧','家庭剧','网络剧','军旅剧']    
         
        #http://search.video.qiyi.com/o?pageNum=1&mode=11&ctgName=电视剧&threeCategory=&pageSize=50&type=list&if=html5&pos=1&site=iqiyi&access_play_control_platform=15
        #for category in categories:
            #self.start_urls.append('http://search.video.qiyi.com/o?pageNum=1&mode=11&ctgName=电视剧&threeCategory=%s&pageSize=50&type=list&if=html5&pos=1&site=iqiyi&access_play_control_platform=15'%category)
    
        
    def parse(self, response):
        if re.match('^(http|https|ftp)\://search.video.iqiyi.com/.*',response.url): 
            result = json.loads(response.body_as_unicode())
            if re.search('pageNum=1&',response.url) and result: 
                page_size = int(re.search('pageSize=(\d+)',response.url).group(1))
                total_num = result['data']['result_num'] if  result['data']['result_num']  else 1000
                total_page = total_num/page_size if total_num % page_size == 0 else int(total_num/page_size) + 1 
                for page in range(2,total_page +1):
                    url = re.sub('pageNum=1&','pageNum=%d&' %page,response.url)
                    yield scrapy.Request(url,callback = self.parse,dont_filter = False)
            if 'code' in result['data'] and  result['data']['code'] == 0:
                for item in result['data']['docinfos']: 
                    if 'albumLink' in item['albumDocInfo']:
                        tvplay = TVPlayItem()
                        tvplay["url"] = item['albumDocInfo']['albumLink']
                        tvplay["website"] = 'iqiyi'
                        #"ename":item['albumDocInfo']['albumEnglishTitle'],
                        #tvplay["score"] = item['albumDocInfo']['score']
                        tvplay["area"] = item['albumDocInfo']['region']
                        tvplay["aid"] = item['albumDocInfo']['albumId']
                        tvplay["playdate"] =  str(datetime.today())
                        tvplay["directors"] = item['albumDocInfo']['director'] if 'director' in item['albumDocInfo'] else ''
                        tvplay["actors"] = item['albumDocInfo']['star'] if 'star' in item['albumDocInfo'] else ''
                        tvplay["episodes"] = item['albumDocInfo']['itemTotalNumber']
                        tvplay["playStatus"] = item['albumDocInfo']['playTime'] if 'playTime' in item['albumDocInfo'] else ''
                        tvplay["releaseDate"] = item['albumDocInfo']['releaseDate']
                        tvplay["genre"] = ','.join(item['albumDocInfo']['video_lib_meta']['category']) if 'category' in item['albumDocInfo']['video_lib_meta']   else ''
                        #tvplay["tags"] = re.sub(',\d+','',item['albumDocInfo']['threeCategory']).replace(' ',',')
                        tvplay["desc"] = item['albumDocInfo']['video_lib_meta']['description'] if 'description' in item['albumDocInfo']['video_lib_meta'] else ''
                        tvplay["name"] = item['albumDocInfo']['albumTitle']
                        if "playCount" in item['albumDocInfo']:
                            tvplay["playCount"] = item['albumDocInfo']['playCount']
                        tvplay["cover_img_sm"] = item['albumDocInfo']['albumHImage']
                        try:
                            tvplay["lastepisode"] = item['albumDocInfo']['newest_item_number']
                        except:
                            tvplay["lastepisode"] = 0
                        tvplay["cover_img"] = item['albumDocInfo']['video_lib_meta']['poster'] if 'poster' in item['albumDocInfo']['video_lib_meta'] else None
                        #yield tvplay
                        
                        if 'videoinfos' in item['albumDocInfo'] and len(item['albumDocInfo']['videoinfos'])>0:
                            videoid = item['albumDocInfo']['videoinfos'][0]['tvId']
                            request = scrapy.Request('https://pcw-api.iqiyi.com/video/video/hotplaytimes/%s/'%tvplay["aid"],callback = self.renqi_parse,dont_filter = False)
                            request.meta['tvplay'] = tvplay
                            yield request 
                        else:
                            #request = scrapy.Request('http://cache.video.qiyi.com/jp/pc/%s/'%tvplay["aid"],callback = self.stats_parse,dont_filter = False)
                            request = scrapy.Request('https://pcw-api.iqiyi.com/video/video/hotplaytimes/%s/'%tvplay["aid"],callback = self.renqi_parse,dont_filter = False)
                            request.meta['tvplay'] = tvplay
                            yield request
                        
            else:
                logging.warning("Cannt get videolist:%s"%response.url)
        else:
            tvplay = TVPlayItem()
            aid = re.search('albumId: (\d+),',response.body_as_unicode()).group(1)
            tvplay["website"] = 'iqiyi'
            tvplay['aid'] = aid
            tvplay['url'] = response.url
            name = re.search('<title>([^-]+)\-.*</title>',response.body_as_unicode()).group(1)
            tvplay['name'] = name
            tvplay["playdate"] =  str(datetime.today())
            request = scrapy.Request('http://cache.video.qiyi.com/jp/pc/%s/'%aid,callback = self.stats_parse,dont_filter = False)
            request.meta['tvplay'] = tvplay
            yield request
            
    def stats_parse(self,response):
        tvplay = response.meta['tvplay']
        result = json.loads(response.body_as_unicode())
        if result['code'] == 'A00000' and 'data' in result:
            tvplay['playCount'] = result['data']['playcnt']
        request = scrapy.Request('https://pcw-api.iqiyi.com/video/video/hotplaytimes/%s/'%tvplay["aid"],callback = self.renqi_parse,dont_filter = False)
        request.meta['tvplay'] = tvplay
        yield request
        #yield tvplay

    def newstats_parse(self,response):
        tvplay = response.meta['tvplay']
        tvplay['playCount'] = re.search('"playCount":(\d+)',response.body_as_unicode()).group(1)
        request = scrapy.Request('https://pcw-api.iqiyi.com/video/video/hotplaytimes/%s/'%tvplay["aid"],callback = self.renqi_parse,dont_filter = False)
        request.meta['tvplay'] = tvplay
        yield request

    def renqi_parse(self,response):
        tvplay = response.meta['tvplay']
        tvplay['renqi'] = re.search('"hot":(\d+)',response.body_as_unicode()).group(1)
        yield tvplay