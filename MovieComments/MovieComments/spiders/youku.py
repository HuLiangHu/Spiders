# -*- coding: utf-8 -*-
import execjs
from datetime import datetime
import re
import scrapy
import time
import json
from urllib.parse import urlencode

from MovieComments.items import MoviecommentsItem



class YoukuSpider(scrapy.Spider):
    name = 'youku'
    allowed_domains = ['youku.com']
    start_urls = ['http://youku.com/']
    baseurl = 'https://p.comments.youku.com/ycp/comment/pc/commentList?'
    custom_settings = {
        'Host':'p.comments.youku.com',
        #'Referer': 'http://v.youku.com/v_show/id_XMzgyNzQxNTkxNg==.html?spm=a2hww.11359951.m_26657.5~5~1~3!2~A',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }

    def getSign(self,timestamp):

        t = '100-DDwODVkv&6c4aa6af6560efff5df3c16c704b49f1&{}'.format(timestamp)
        with open("MovieComments/youku.js") as f:
            jsData = f.read()

        js = execjs.compile(jsData)
        sign = js.call('test()', t)
        return sign
    def start_requests(self):
        start_url ='http://list.youku.com/category/show/c_97_r_2019_pt_0_s_4_d_1.html?spm=a2h1n.8251845.filterPanel.5!6~1~3~A'
        yield scrapy.Request(start_url,callback=self.parse_pre_video)

    def parse_pre_video(self,response):

        for info in response.xpath('//ul[@class="panel"]/li'):
            tempurl=info.xpath('.//a/@href').extract_first()
            if 'http:' in tempurl:
                url = tempurl
            else:
                url ='https:'+tempurl
            title =info.xpath('.//a/@title').extract_first()
            yield scrapy.Request(url,callback=self.parse_albumurl,meta={'title':title},dont_filter=False)

    def parse_albumurl(self,response):
        albumurl = 'https:' + response.xpath('//h1/span/a/@href').extract_first()
        yield scrapy.Request(albumurl, callback=self.parse_albumId, meta={'title': response.meta['title'],'albumurl':albumurl}, dont_filter=False)

    def parse_albumId(self,response):
        showid = re.search('showid:\"(\d+)\"', response.text).group(1)
        title = response.xpath('//div[@class="p-thumb"]/a/@title').extract_first()
        url = 'https://list.youku.com/show/episode?id={}&stage=reload1&callback=jQuery'.format(showid)
        yield scrapy.Request(url, callback=self.parse_videourl,meta={'title': title,
                                                                     'albumurl': response.meta['albumurl']})

    def parse_videourl(self,response):
        videourls = re.findall('href=\\\\".*?id_(.*?)\.html.*?\\\\" target=\\\\"_blank\\\\">\d+<\\\/a>', response.text)
        episodes = re.findall('href=\\\\".*?\\\\" target=\\\\"_blank\\\\">(\d+)<\\\/a>', response.text)
        for videourl, episode in zip(videourls, episodes):
            videourl = 'https://v.youku.com/v_show/id_' + videourl
            yield scrapy.Request(videourl , callback=self.parse_tvid,meta={'videourl':videourl,
                                                                            'episode':episode,
                                                                           'title':response.meta['title'],
                                                                           'albumurl': response.meta['albumurl']})
    def parse_tvid(self,response):
        tvid = re.search('videoId: \'(\d+)\',',response.text).group(1)
        videourl = 'http://v.youku.com/v_show/id_{}'.format(re.search('videoId2: \'(.*?)\',',response.text).group(1))
        tiemstemp =int(time.time())

        #episode = int(info['next']['seq'])-1
        parmas = {
            'app': '100-DDwODVkv',
            'objectId': tvid,
            'objectType': '1',
            'listType': '0',
            'currentPage': '1',
            'pageSize': '30',
            'sign': self.getSign(tiemstemp),
            'time': tiemstemp
        }
        # 橙红年代

        url = self.baseurl + urlencode(parmas)
        # #
        yield scrapy.Request(url, meta={'parmas': parmas,
                                        'title':response.meta['title'],
                                        'episode': response.meta['episode'],
                                        'albumurl': response.meta['albumurl'], 'videourl': videourl}, callback=self.parse_parmas,
                             dont_filter=False)
    def parse_parmas(self,response):
        maxpage = json.loads(response.text)['data']['totalPage']
        for page in range(1,int(maxpage)+1):
            parmas = response.meta['parmas']
            parmas['currentPage'] = page

            #橙红年代
            url = self.baseurl+urlencode(parmas)

            yield scrapy.Request(url,meta={'title':response.meta['title'],'episode':response.meta['episode'],'albumurl':response.meta['albumurl'],'videourl':response.meta['videourl']},dont_filter=True)

    def parse(self, response):
        for info in json.loads(response.text)['data']['comment']:
            item = MoviecommentsItem()
            item['albumurl'] = response.meta['albumurl']
            item['comment'] = info['content']
            comment_time = info['createTime']
            item['comment_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(comment_time/1000)))
            item['commentId'] = info['id']
            item['author'] = info['user']['userName']
            item['title'] =str(response.meta['title']).split(' ')[0]
            item['episode'] = response.meta['episode']
            item['videourl'] = response.meta['videourl']
            item['ctime'] = str(datetime.now()).split('.')[0]
            item['site'] ='youku'
            yield item
