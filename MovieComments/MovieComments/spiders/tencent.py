# -*- coding: utf-8 -*-
import re
from datetime import datetime

import json
import scrapy
import time
import requests
from MovieComments.items import MoviecommentsItem
from scrapy import Selector
from urllib.parse import urlencode


class TencentSpider(scrapy.Spider):
    name = 'tencent'
    #allowed_domains = ['v.qq.com']
    #详情页
    start_urls = ['https://v.qq.com/x/bu/pagesheet/list?_all=1&append=1&channel=tv&listpage=2&offset=0&pagesize=24&sort=18']
    baseurl ='http://s.video.qq.com/get_playsource?'
    timestemp = int(time.time() * 1000)
    episode_number =87
    try:
        cid = re.search('http.*://v.qq.com/detail/.*?/(.*).html',start_urls[0]).group(1)
    except:
        pass
    headers={
        'Host': 's.video.qq.com',
        #'Referer': 'http://v.qq.com/detail/1/1wbx6hb4d3icse8.html',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }

    def parse(self, response):
        for info in response.xpath('//div[@class="list_item"]'):
            video_detail =info.xpath('./a/@href').extract_first()

            video_detail_cid = re.search(r'https://v.qq.com/x/cover/(.*?).html',video_detail).group(1)
            video_detail_url ='https://v.qq.com/detail/1/{}.html'.format(video_detail_cid)

            yield scrapy.Request(video_detail_url,callback=self.parse_video,meta={'albumurl':video_detail_url})

######################
    # def parse(self, response):
    #
    #     """
    #     综艺
    #     :param response:
    #     :return:
    #     """
    #     for i in response.xpath('//li[@class="list_item"]'):
    #         url = i.xpath('a/@href').extract_first()
    #         title = i.xpath('a/@title').extract_first()
    #
    #         yield scrapy.Request(url,callback=self.parse_commentid,meta={'title':title})
    #
    # def parse_commentid(self,response):
    #     vid = re.search('vid=(.*)',response.url).group(1)
    #     parmas ={
    #         'otype': 'json',
    #         'op': '3',
    #         'vid': vid
    #     }
    #     url = 'https://ncgi.video.qq.com/fcgi-bin/video_comment_id?'+urlencode(parmas)
    #
    #     yield scrapy.Request(url, callback=self.parse_next_video, meta={'title': response.meta['title']})


#################################


    def parse_video(self, response):
        title =response.xpath('//h1[@class="video_title_cn"]/a/text()').extract_first()
        cid=re.search('http.*://v.qq.com/detail/.*?/(.*).html',response.url).group(1)
        parmas = {
            'id': cid,
            'plat': '2',
            'type': '4',
            'data_type': '2',
            'video_type': '2',
            'range': '1-{}'.format(self.episode_number),
            'plname': 'qq',
            'otype': 'json',
            'num_mod_cnt': '20',
            '_t': self.timestemp
        }
        url = self.baseurl+urlencode(parmas)
        # print(url)
        yield scrapy.Request(url, callback=self.parse_pre_url,headers=self.headers,meta={'albumurl':response.meta['albumurl'],'title':title},dont_filter=False)

    def parse_pre_url(self,response):
        # print(response.text)
        infos = re.search('QZOutputJson=(.*);',response.text).group(1)
        # print(json.loads(infos)['PlaylistItem'])
        for info in json.loads(infos)['PlaylistItem']['videoPlayList']:
            vid = info['id']
            episode = info['episode_number']
            link = info['playUrl']
            #print(link)
            baseurl = 'https://ncgi.video.qq.com/fcgi-bin/video_comment_id?'
            parmas = {
                'otype': 'json',
                'op': '3',
                'vid': vid,
                '_': int(time.time())
            }

            url = baseurl + urlencode(parmas)

            yield scrapy.Request(url,meta = {'episode': episode,'albumurl':response.meta['albumurl'],'title':response.meta['title'],'videourl':link},callback=self.parse_next_video,dont_filter=False)


    def parse_next_video(self,response):

        commentid = re.search('"comment_id":"(\d+)"',response.text).group(1)
        parmas ={
            'orinum': '10',
            'oriorder': 'o',
            'pageflag': '1',
            'cursor': '0',
            'scorecursor': '0',
            'orirepnum': '2',
            'reporder': 'o',
            'reppageflag': '1',
            'source': '9',
            '_': self.timestemp
        }
        url ='https://video.coral.qq.com/varticle/{}/comment/v2?'.format(commentid)+urlencode(parmas)
        yield scrapy.Request(url,meta={'parmas':parmas,'url':url,'title':response.meta['title'],'episode':response.meta['episode'],'albumurl':response.meta['albumurl'],'videourl':response.meta['videourl']},callback=self.parse_next_commentpage,dont_filter=False)


    def parse_next_commentpage(self, response):
        data =json.loads(response.text)
        targetid = data['data']['targetid']
        parmas = response.meta['parmas']
        parmas['cursor'] = int(data['data']['last'])
        parmas['_'] = self.timestemp
        for info in data['data']['oriCommList']:
            item = MoviecommentsItem()
            item['albumurl'] =response.meta['albumurl']
            item['comment'] = info['content']
            item['author'] = info['userid']
            comment_time =info['time']
            item['comment_time'] =time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(comment_time)))
            item['commentId'] = info['id']
            item['ctime'] = str(datetime.now())
            item['title'] = str(response.meta['title'])
            item['episode'] = str(response.meta['episode'])
            item['site'] = 'tencent'
            item['videourl'] = response.meta['videourl']
            yield item
        url = 'https://video.coral.qq.com/varticle/{}/comment/v2?'.format(targetid) + urlencode(parmas)
        yield scrapy.Request(url, meta={'parmas': parmas,'title':response.meta['title'],'episode':response.meta['episode'],'albumurl':response.meta['albumurl'],'videourl':response.meta['videourl']},callback=self.parse_next_commentpage)



