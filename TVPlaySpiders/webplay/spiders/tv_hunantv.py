# -*- coding: utf-8 -*-
import scrapy
import json
import re
from datetime import datetime
from webplay.items import TVPlayItem
import logging

class HunanTVSpider(scrapy.Spider):
    name = "tv_hunantv"
    #'http://v5m.api.mgtv.com/remaster/listV5/search?fstlvlId=2&ic=1&pageNum=1&pageSize=30&kind=a4',
    start_urls = ( 
        'http://pianku.api.mgtv.com/rider/list/mobile?chargeInfo=a1&area=a3&pn=1&kind=a4&uid=&fstlvlId=2&sort=c1&type=10',
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
            tvplay = TVPlayItem()
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
            tvplay = TVPlayItem()
            tvplay['url'] = albumurl
            tvplay['aid'] = aid
            #tvplay['tvplayid'] = md5(albumurl)
            tvplay['name'] = item['clipName']
            # tvplay['episodes'] = item['videoIndex']
            tvplay['lastepisode'] = item['videoIndex']
            #print(item['intro'])
            if r'导演' in str(item['intro']):
                tvplay['directors'] = re.search('导演：(.*?)\'', str(item['intro'])).group(1)
            if r'演员' in str(item['intro']):
                tvplay['actors'] = re.search('\演员：(.*?)\'',str(item['intro'])).group(1)
            tvplay['cover_img'] = response.meta['cover_img']
            if r'简介' in str(item['intro']):
                tvplay['desc'] = re.search('简介：(.*?)\'',str(item['intro'])).group(1)
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
        result = json.loads(response.text)
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

