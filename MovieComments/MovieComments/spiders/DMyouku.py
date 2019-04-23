# -*- coding: utf-8 -*-
from datetime import datetime

import scrapy
import re
from urllib.parse import urlencode
import json
import time
import random
'https://service.danmu.youku.com/list?mat=6&mcount=1&ct=1001&iid=1035192760&aid=333760&cid=97&lid=0&ouid=0&_=1555904229914'
'https://service.danmu.youku.com/list?mat=44&mcount=1&ct=1001&iid=1036877901&aid=333760&cid=97&lid=0&ouid=0&_=1555904683'
class DmyoukuSpider(scrapy.Spider):
    name = 'DMyouku'
    # allowed_domains = ['youku.com']
    start_urls = ['https://list.youku.com/show/id_z2253d237991f4c78852a.html?spm=a2h0j.11185381.bpmodule-playpage-lefttitle.5~5~H1~8~A']
    baseurl='https://service.danmu.youku.com/list?'


    def parse(self, response):
        showid = re.search('showid:\"(\d+)\"', response.text).group(1)
        title = response.xpath('//div[@class="p-thumb"]/a/@title').extract_first()
        url = 'https://list.youku.com/show/episode?id={}&stage=reload1&callback=jQuery'.format(showid)
        yield scrapy.Request(url,callback=self.parse_videourl,meta={'title':title,
                                                                    'showid':showid})

    def parse_videourl(self, response):
        videourls = re.findall('href=\\\\".*?id_(.*?)\.html.*?\\\\" target=\\\\"_blank\\\\">\d+<\\\/a>', response.text)
        episodes = re.findall('href=\\\\".*?\\\\" target=\\\\"_blank\\\\">(\d+)<\\\/a>', response.text)
        for videourl, episode in zip(videourls, episodes):
            # print(videourl,episode)
            videourl = 'https://v.youku.com/v_show/id_' + videourl
            yield scrapy.Request(videourl, callback=self.parse_parmas, meta={'videourl': videourl,
                                                                           'episode': episode,
                                                                           'showid':response.meta['showid'],
                                                                           'title': response.meta['title']})


    def parse_parmas(self, response):
        """
        :param response:
        :return: iid=vid;aid=showid,cid=videoCategoryId
        """
        aid = response.meta['showid']
        cid = re.search('videoCategoryId: \'(\d+)\'', response.text).group(1)
        vid = re.search('videoId: \'(\d+)\'',response.text).group(1)

        comment_time =0
        for i in range(0,45):
            comment_time += 59
            parmas = {
                'mat': i,
                'mcount': '1',
                'ct': '1001',
                'iid': vid,
                'aid': aid,
                'cid': cid,
                'lid': '0',
                'ouid': '0',
                '_': str(int(time.time())+60)
            }
            url = self.baseurl + urlencode(parmas)
            yield scrapy.Request(url, meta={'parmas': parmas,'episode': response.meta['episode'],'title':response.meta['title'],'comment_time':self.parsetime(str((i)*60))+'--'+str(i)+'分59秒'},callback=self.parse_item)



    def parse_item(self, response):
        for info in json.loads(response.text)['result']:
            item = {}
            item['comment'] = info['content']
            comment_time = info['createtime']
            item['comment_time'] = str(response.meta['comment_time'])
            item['pub_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(comment_time / 1000)))
            item['authorid'] = info['uid']
            item['title'] = response.meta['title']
            item['episode'] = response.meta['episode']
            item['ctime'] = str(datetime.now())
            yield item

    def parsetime(self,time):
        return str(int(int(time)/60))+'分'+str(int(int(time)%60))+'秒'

