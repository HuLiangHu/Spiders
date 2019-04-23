# -*- coding: utf-8 -*-
import scrapy
import json
import re
from datetime import datetime
from variety.items import VarietyItem,VarietyVideoItem
import logging
class HunanTVSpider(scrapy.Spider):
    name = "variety_hunantv"
    start_urls = ( 'http://pianku.api.mgtv.com/rider/list/mobile?chargeInfo=a1&area=a3&pn=1&kind=a4&uid=&fstlvlId=1&sort=c1&type=10',
    )

    def parse(self, response):
        if  re.match('^(http|https|ftp)\:\/\/pianku.api.mgtv.com\/rider\/list\/mobile',response.url):
            result = json.loads(response.body_as_unicode())
            if len(result['data']['hitDocs'])>0:
                for item in result['data']['hitDocs']: 
                    #albumn = {}
                    #http://v.api.hunantv.com/web/multivv?cids=150115
                    #albumid = re.search('www.hunantv.com/v/2/(\d+)/',item['url']).group(1)
                    vid =  item['playPartId'] #url: "#/b/313702/3904293"
                    cover_img = item['img']
                    # url = 'http://m.api.hunantv.com/video/getbyid?videoId=%s'%vid
                    url =  'http://v5m.api.mgtv.com/remaster/vrs/getByPartId?partId=%s' %vid #'http://v5m.api.mgtv.com/vrs/getByPartId?partId=%s' % vid
                    request = scrapy.Request(url,callback = self.detail_parse,priority=1,dont_filter = False)
                    request.meta['cover_img'] = cover_img
                    yield request
                page = int(re.search('pn=(\d+)',response.url).group(1))
                url = re.sub('pn=\d+','pn=%s' %(page+1),response.url)
                yield scrapy.Request(url,callback = self.parse,dont_filter = False)
        elif  re.match('^(http|https|ftp)\:\/\/v5m.api.mgtv.com\/remaster\/listV5\/search',response.url):
            result = json.loads(response.body_as_unicode())
            if len(result['data'])>0:
                for item in result['data']: 
                    #albumn = {}
                    #http://v.api.hunantv.com/web/multivv?cids=150115
                    #albumid = re.search('www.hunantv.com/v/2/(\d+)/',item['url']).group(1)
                    vid = re.search('#/b/\d+/(\d+)',item['url']).group(1) #url: "#/b/313702/3904293"
                    cover_img = item['image']
                    # url = 'http://m.api.hunantv.com/video/getbyid?videoId=%s'%vid
                    url =  'http://v5m.api.mgtv.com/remaster/vrs/getByPartId?partId=%s' % vid #'http://v5m.api.mgtv.com/vrs/getByPartId?partId=%s' % vid
                    request = scrapy.Request(url,callback = self.detail_parse,priority=1,dont_filter = False)
                    request.meta['cover_img'] = cover_img
                    yield request
                page = int(re.search('pageNum=(\d+)',response.url).group(1))
                url = re.sub('pageNum=\d+','pageNum=%s' %(page+1),response.url)
                yield scrapy.Request(url,callback = self.parse,dont_filter = False)
        else:
            name  = re.search('cname: "(.+)"',response.body_as_unicode()).group(1)
            aid  = re.search('cid: (\d+),',response.body_as_unicode()).group(1)
            tvplay = VarietyItem()
            tvplay['url'] = response.url
            tvplay['aid'] = aid
            #tvplay['tvplayid'] = md5(albumurl)
            tvplay['name'] = name
            tvplay['website'] = 'hunantv'
            url = 'http://vc.mgtv.com/v2/dynamicinfo?cid=%s' %aid
            request = scrapy.Request(url,callback = self.stats_parse,priority=2,dont_filter = False)
            request.meta['item'] = tvplay
            yield request

    def detail_parse(self,response):
        result = json.loads(response.body_as_unicode())
        if result['code'] == 200:
            item = result['data']
            aid = item['clipId']
            albumurl =  'http://www.mgtv.com/v/2/%s/' %aid # re.search('(http://www.mgtv.com/v/2/\d+/)',item['pcUrl']).group(1)
            tvplay = VarietyItem()
            tvplay['url'] = albumurl
            tvplay['aid'] = aid
            #tvplay['tvplayid'] = md5(albumurl)
            tvplay['name'] = item['clipName']
            # tvplay['episodes'] = item['videoIndex']
            #tvplay['lastepisode'] = item['videoIndex']
             
           
            tvplay['cover_img'] = response.meta['cover_img']
            if 'story' in item['intro'].keys():
                tvplay['desc'] = ','.join(map(lambda x: x['value'], item['intro']['story']))
            else:
                tvplay['desc'] = ''
            # tvplay['additional_infos'] = { 'productionYear':item['year']} 
            # tvplay['releaseDate'] = item['publishTime'] 
            tvplay['website'] = 'hunantv'
            
            #url = 'http://videocenter-2039197532.cn-north-1.elb.amazonaws.com.cn/dynamicinfo?cid=%s' %aid
            url = 'http://vc.mgtv.com/v2/dynamicinfo?cid=%s' %aid
            request = scrapy.Request(url,callback = self.stats_parse,priority=2,dont_filter = False)
            request.meta['item'] = tvplay
            return request
        else:
            logging.warning('Cannt get video info:%s' %response.url)
    def stats_parse(self,response):
        tvplay = response.meta['item']
        result = json.loads(response.body_as_unicode())
        tvplay['playCount'] = result['data']['all'] 
        '''
        if not 'additional_infos' in tvplay:
            tvplay['additional_infos'] = {}
        tvplay['additional_infos']['mobileVV'] = result['data']['mobileVV']
        tvplay['additional_infos']['msitePadVV'] = result['data']['msitePadVV']
        tvplay['additional_infos']['msitePhoneVV'] = result['data']['msitePhoneVV']
        tvplay['additional_infos']['outsideVV'] = result['data']['outsideVV']
        tvplay['additional_infos']['padVV'] = result['data']['padVV']
        tvplay['additional_infos']['pcClientVV'] = result['data']['pcClientVV']
        tvplay['additional_infos']['pcWebVV'] = result['data']['pcWebVV']
        '''
        tvplay['playdate'] = str(datetime.today())
        return tvplay
  
    def videos_parse(self,response):
        videos = json.loads(response.body_as_unicode())
        variety = response.meta['item']
        for video in videos['data']['list']: 
            url = 'http://m.api.hunantv.com/video/getbyid?videoId=%s' %video['videoId']
            request = scrapy.Request(url,callback = self.video_parse,priority=2) 
            yield request
            
    def video_parse(self,response): 
        videoobj = json.loads(response.body_as_unicode()) 
        videoinfo = VarietyVideoItem()
        videoinfo['url'] = 'http://www.mgtv.com/v/1/%s/f/%s.html' %(videoobj['data']['detail']['collectionId'],videoobj['data']['detail']['videoId'])
        videoinfo['aid'] = videoobj['data']['detail']['collectionId']
        videoinfo['vid'] = videoobj['data']['detail']['videoId']
        videoinfo['albumurl'] = 'http://www.mgtv.com/v/1/%s/' %videoinfo['aid']
        videoinfo['video_img'] = videoobj['data']['detail']['image']
        videoinfo['name'] = videoobj['data']['detail']['name']
        videoinfo['desc'] = videoobj['data']['detail']['v_desc']
        videoinfo['releaseDate'] = videoobj['data']['detail']['publishTime'] 
        videoinfo['website'] = 'hunantv' 
        videoinfo['player'] = videoobj['data']['detail']['player']
        url = 'http://videocenter-2039197532.cn-north-1.elb.amazonaws.com.cn/dynamicinfo?vid=%s' %videoinfo['vid']
        request = scrapy.Request(url,callback = self.stats_parse,priority=3)
        request.meta['item'] = videoinfo
        yield request
      