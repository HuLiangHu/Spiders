# -*- coding: utf-8 -*-
import scrapy
import re
import json
from datetime import datetime
from webplay.items import MovieItem
import logging

class HunanTVSpider(scrapy.Spider):
    name = "movie_hunantv"
    start_urls = ( 
        'http://pianku.api.mgtv.com/rider/list/mobile?chargeInfo=a1&area=a3&pn=1&kind=a4&uid=&fstlvlId=3&sort=c1&type=10',
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
                    request = scrapy.Request(url,callback = self.detail_parse,priority=1)
                    request.meta['cover_img'] = cover_img
                    yield request
                page = int(re.search('pn=(\d+)',response.url).group(1))
                url = re.sub('pn=\d+','pn=%s' %(page+1),response.url)
                yield scrapy.Request(url,callback = self.parse)
        else:
            name  = re.search('cname: "(.+)"',response.body_as_unicode()).group(1)
            aid  = re.search('cid: (\d+),',response.body_as_unicode()).group(1)
            tvplay = MovieItem()
            tvplay['url'] = response.url
            tvplay['aid'] = aid
            #tvplay['tvplayid'] = md5(albumurl)
            tvplay['name'] = name
            tvplay['website'] = 'hunantv'
            url = 'http://vc.mgtv.com/v2/dynamicinfo?cid=%s' %aid
            request = scrapy.Request(url,callback = self.stats_parse,priority=2)
            request.meta['item'] = tvplay
            yield request
     
    def detail_parse(self,response):
        result = json.loads(response.body_as_unicode())
        if result['code'] == 200:
            item = result['data']
            aid = item['clipId']
            albumurl =  'http://www.mgtv.com/h/%s.html' %aid # re.search('(http://www.mgtv.com/v/2/\d+/)',item['pcUrl']).group(1)
            tvplay = MovieItem()
            tvplay['url'] = albumurl
            tvplay['aid'] = aid
            #tvplay['tvplayid'] = md5(albumurl)
            tvplay['name'] = item['clipName']
            if 'director' in item['intro'].keys():
                tvplay['directors'] = ','.join(map(lambda x: x['value'], item['intro']['director']))
            if 'leader' in item['intro'].keys():
                tvplay['actors'] = ','.join(map(lambda x: x['value'], item['intro']['leader']))
            tvplay['cover_img'] = response.meta['cover_img']
            if 'story' in item['intro'].keys():
                tvplay['desc'] = ','.join(map(lambda x: x['value'], item['intro']['story']))
            else:
                tvplay['desc'] = ''
            # tvplay['additional_infos'] = { 'productionYear':item['year']} 
            # tvplay['releaseDate'] = item['publishTime'] 
            tvplay['website'] = 'hunantv'
            url = 'http://vc.mgtv.com/v2/dynamicinfo?cid=%s' %aid
            request = scrapy.Request(url,callback = self.stats_parse,priority=2)
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