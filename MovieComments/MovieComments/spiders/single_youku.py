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
    name = 'single_youku'
    allowed_domains = ['youku.com']
    start_urls = [
        'https://v.youku.com/v_show/id_XNDA2ODQ5ODY2NA==.html?tpa=dW5pb25faWQ9MTAzNzUzXzEwMDAwMV8wMV8wMQ&refer=baiduald1705'
    ]
    baseurl = 'https://p.comments.youku.com/ycp/comment/pc/commentList?'
    custom_settings = {
        'Host':'p.comments.youku.com',
        #'Referer': 'http://v.youku.com/v_show/id_XMzgyNzQxNTkxNg==.html?spm=a2hww.11359951.m_26657.5~5~1~3!2~A',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }

    def getSign(self,timestamp):

        t = '100-DDwODVkv&6c4aa6af6560efff5df3c16c704b49f1&{}'.format(timestamp)
        with open("spiders/youku.js") as f:
            jsData = f.read()

        js = execjs.compile(jsData)
        sign = js.call('test()', t)
        return sign
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url,callback=self.parse_albumId)

    def parse_albumId(self,response):
        showid = re.search('showid:\"(\d+)\"', response.text).group(1)
        title = response.xpath('//div[@class="p-thumb"]/a/@title').extract_first()
        url = 'https://list.youku.com/show/episode?id={}&stage=reload&callback=jQuery'.format(showid)
        yield scrapy.Request(url, callback=self.parse_videourl,meta={'title': title})

    def parse_videourl(self,response):
        videourls = re.findall('href=\\\\".*?id_(.*?)\.html.*?\\\\" target=\\\\"_blank\\\\">\d+<\\\/a>', response.text)
        episodes = re.findall('href=\\\\".*?\\\\" target=\\\\"_blank\\\\">(\d+)<\\\/a>', response.text)
        for videourl, episode in zip(videourls, episodes):

            videourl = 'https://v.youku.com/v_show/id_' + videourl
            episode = episode
            yield scrapy.Request(videourl , callback=self.parse_tvid,meta={'videourl':videourl,
                                                                            'episode':episode,
                                                                           'title':response.meta['title']})
###########
#     def start_requests(self):
#         """
#         电影
#         :return:
#         """
#         title ='大人物'
#         for url in self.start_urls:
#             yield scrapy.Request(url,callback=self.parse_tvid,meta={'title':title,'episode':None})
############

    def parse_tvid(self,response):
        tvid = re.search('videoId: \'(\d+)\',',response.text).group(1)

        albumurl = 'https://list.youku.com/show/id_z8a7ef73d07e5496396d4.html?spm=a2h0j.11185381.bpmodule-playpage-righttitle.5~H2~A'
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
                                        'albumurl': albumurl, 'videourl': videourl}, callback=self.parse_parmas,
                             dont_filter=False)

    def parse_parmas(self,response):

        maxpage = json.loads(response.text)['data']['totalPage']
        for page in range(1,int(maxpage)+1):
            parmas = response.meta['parmas']
            parmas['currentPage'] = page

            #橙红年代
            url = self.baseurl+urlencode(parmas)

            yield scrapy.Request(url, meta={'title': response.meta['title'], 'episode': response.meta['episode'],
                                            'albumurl': response.meta['albumurl'],
                                            'videourl': response.meta['videourl']}, dont_filter=True)

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



