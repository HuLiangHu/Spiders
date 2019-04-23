# -*- coding: utf-8 -*-
from datetime import datetime
from urllib.parse import urlencode

import scrapy
import time
import json
import re
import requests
import random

from MovieComments.items import MoviecommentsItem


class MgtvSpider(scrapy.Spider):
    name = 'mgtv'
    #allowed_domains = ['mangguo.com']
    #详情页链接
    start_urls = ['https://list.mgtv.com/2/a1-a1--------c2-1---.html?channelId=2']
    commentapi ='https://comment.mgtv.com/v4/comment/getCommentList?'
    videoapi ='https://pcweb.api.mgtv.com/episode/list?'#每个视频链接

    headers ={
        #'referer': 'https://www.mgtv.com/b/326018/4572558.html',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
    }

    def getTotalPage(self,url):
        response = requests.get(url,headers=self.headers)
        totalpage = response.json()['data']['commentCount']
        return totalpage/15

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0],headers=self.headers)
    def parse(self,response):

        for info in response.xpath('//li[@class="m-result-list-item"]')[:25]:
            video_url = info.xpath('./a/@href').extract_first()
            title = info.xpath('./a/img/@alt').extract_first()
            video_detail_url ='https://www.mgtv.com/h/{}.html'.format(re.search('(\d+)',video_url).group(1))
            yield scrapy.Request(video_detail_url,callback=self.parse_per_video,meta={'albumurl':video_detail_url,'title':title})
    def parse_per_video(self,response):

        #综艺
#####################
        # subjectId = re.search('.*\/(\d+)', self.start_urls).group(1)
        # parmas = {
        #     'subjectType': 'hunantv2014',
        #     'subjectId': subjectId,
        #     '_support': '10000000',
        #     '_': int(time.time() * 1000) + random.randint(3000, 8000),
        # }
        # title = '快乐大本营20181027期'
        # for page in range(1, 100):
        #     parmas['page'] = page
        #     url = self.commentapi + urlencode(parmas)
        #     yield scrapy.Request(url, meta={'title': title})
##########################################

        #电视剧
        collection_id = re.search('(\d+)',response.url).group(1)
        parmas ={
            'collection_id': collection_id,
            'page': '1',
        }
        url = self.videoapi+urlencode(parmas)
        yield scrapy.Request(url,callback=self.parse_prevideolink,meta={'albumurl':response.meta['albumurl'],'title':response.meta['title'],'parmas':parmas})

    #####################
    def parse_prevideolink(self, response):
        total_page =json.loads(response.text)['data']['total_page']
        for info in json.loads(response.text)['data']['list']:
            subjectId = re.search('.*\/(\d+)', info['url']).group(1)
            episode = info['t4']
            comment_parmas = {
                'subjectType': 'hunantv2014',
                'subjectId': subjectId
            }
            ###########
            #剧集
            url = self.commentapi + urlencode(comment_parmas)
            yield scrapy.Request(url, callback=self.parse_item, meta={'title': response.meta['title'],
                                                                      'episode': episode,
                                                                      'albumurl': response.meta['albumurl'],
                                                                      'comment_parmas': comment_parmas}, dont_filter=False)
        parmas = response.meta['parmas']
        if int(parmas['page']) < total_page:
            parmas['page'] = str(int(parmas['page']) + 1)
            url = self.videoapi + urlencode(parmas)
            yield scrapy.Request(url, callback=self.parse_prevideolink, meta={'albumurl':response.meta['albumurl'],'title':response.meta['title'],'parmas': parmas})

    def parse_item(self, response):
        for info in json.loads(response.text)['data']['list']:
            item = MoviecommentsItem()
            item['albumurl'] = response.meta['albumurl']
            item['title'] =response.meta['title']
            item['comment'] = info['content']
            item['commentId'] = info['commentId']
            item['author'] = info['user']['nickName']
            comment_time= info['date']
            ctime = int(time.time())

            try:
                comment_time_stemp = self.date_convert(comment_time,ctime)
                item['comment_time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(comment_time_stemp))
            except TypeError:
                comment_times = re.findall('(\d+)',comment_time)
                if len(comment_times)<3:
                    item['comment_time'] = str(time.strftime('%Y',time.localtime(ctime)))+'-'+'-'.join(comment_times)
                else:
                    item['comment_time'] = '-'.join(comment_times)
            item['ctime'] = str(datetime.now()).split('.')[0]
            item['episode'] = re.search('(\d+)',response.meta['episode']).group(1)
            item['videourl'] = info['shareInfo']['url']
            item['site'] = 'mgtv'
            item['ctime'] = str(datetime.now()).split('.')[0]
            yield item

        total_comment_count = int(json.loads(response.text)['data']['commentCount'])
        total_comment_page = int(total_comment_count)//15 + 1
        comment_parmas = response.meta['comment_parmas']
        #print(total_comment_count)
        if total_comment_page <100:
            total_comment_page=total_comment_page
        else:
            total_comment_page =100
        for page in range(1, total_comment_page+ 1):
            comment_parmas['page'] = page
            url = self.commentapi + urlencode(comment_parmas)
            yield scrapy.Request(url, callback=self.parse_item, meta={'title': response.meta['title'],
                                                                      'episode': response.meta['episode'],
                                                                      'albumurl': response.meta['albumurl'],
                                                                      'comment_parmas': comment_parmas},
                                 dont_filter=False)

    def date_convert(self, time, ctime):
        if '分钟' in time:
            data = re.search('(\d+)', time).group(1)
            comment_time_stemp = ctime - int(data) * 60
        elif '小时' in time:
            data = re.search('(\d+)', time).group(1)
            comment_time_stemp = ctime - int(data) * 60 * 60
        elif '天' in time:
            data = re.search('(\d+)', time).group(1)
            comment_time_stemp = ctime - int(data) * 60 * 60 * 24
        elif '刚刚' in time:
            comment_time_stemp = ctime
        else:
            comment_time_stemp = time
        return comment_time_stemp