# -*- coding: utf-8 -*-
import time

import requests
from datetime import datetime
import json
import scrapy
from scrapy import Selector
from urllib.parse import urlencode
import re
from MovieComments.items import MoviecommentsItem


class IqiyiSpider(scrapy.Spider):
    name = 'iqiyi'
    allowed_domains = ['iqiyi.com']
    start_urls=['http://top.iqiyi.com/dianshiju.html']
    commentapi = 'https://sns-comment.iqiyi.com/v3/comment/get_comments.action?'

    headers = {
        'Connection': 'keep-alive',
        'Cookie': 'QC005=e287ee06b869056d8becc26449a2679e; QC006=3faa55072750552fae5a8013cdc71d1f; T00404=5fd38e10416604f8ab178c8b03c9f007; QP001=1; QC173=0; QC118=%7B%22color%22%3A%22FFFFFF%22%2C%22channelConfig%22%3A0%7D; P00004=-542709893.1531018503.cc4c9a0259; nu=0; QP0010=1; QP0012=1; QC157=skip; Hm_lvt_53b7374a63c37483e5dd97d78d9bb36e=1534422382; QC007=DIRECT; QC008=1531017903.1531994081.1534422382.3; QC159=%7B%22color%22%3A%22FFFFFF%22%2C%22channelConfig%22%3A1%2C%22isOpen%22%3A1%2C%22speed%22%3A13%2C%22density%22%3A30%2C%22opacity%22%3A86%2C%22isFilterColorFont%22%3A0%2C%22proofShield%22%3A1%2C%22forcedFontSize%22%3A24%2C%22isFilterImage%22%3A1%7D; QP007=240; QC160=%7B%22u%22%3A%22%22%2C%22lang%22%3A%22%22%2C%22local%22%3A%7B%22name%22%3A%22%E4%B8%AD%E5%9B%BD%E5%A4%A7%E9%99%86%22%2C%22init%22%3A%22Z%22%2C%22rcode%22%3A48%2C%22acode%22%3A86%7D%7D; QC001=1; QC124=1%7C0; _ga=GA1.2.1562739982.1536135625; _gid=GA1.2.264593927.1536135625; PCAU=0; QC021=%5B%7B%22key%22%3A%22%E5%A4%A9%E7%9B%9B%E9%95%BF%E6%AD%8C%22%7D%2C%7B%22key%22%3A%22%E5%BB%B6%E7%A6%A7%E6%94%BB%E7%95%A5%22%7D%5D; Hm_lpvt_53b7374a63c37483e5dd97d78d9bb36e=1536198898; QC010=195333487; __dfp=a0010c3db260e54c8f84af160266968a6cb1c086290e986be01dccae460e735bdf@1537431610035@1536135610035',
        'Host': 'sns-comment.iqiyi.com',
        'Referer': 'http://www.iqiyi.com/lib/m_215034614.html?src=search',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }

    def parse(self,response):
        """

        :param response:
        :return:
        """
        for albumurl in response.xpath('//dl/dt/a/@href').extract()[:25]:
            albumurl ='http:'+albumurl
            yield scrapy.Request(albumurl,callback=self.parse_albumId,meta={'albumurl':albumurl})

    def parse_albumId(self,response):
        """

        :param response:
        :return:获取电视剧albumID
        """
        albumId = re.search('albumId: \"(\d+)\"',response.text).group(1)
        url='https://pcw-api.iqiyi.com/albums/album/avlistinfo?aid={}&page=1&size=100'.format(albumId)
        yield scrapy.Request(url, callback=self.parse_all_video_tvid, meta={'albumurl': response.meta['albumurl']})

    def parse_all_video_tvid(self,response):
        """

        :param response:
        :return: 每集的tvid
        """
        for info in json.loads(response.text)['data']['epsodelist']:
            #print(info)
            title = re.search('(.*?)第',info['name']).group(1)
            episode = info['order']
            videourl = info['playUrl']
            #print(title)
            tvId = info['tvId']
            parmas = {
                'agent_type': '118',
                'agent_version': '9.0.0',
                'authcookie': 'null',
                'business_type': '17',
                'content_id': tvId,
                'hot_size': '0',
                'last_id': '',
                'page': '1',
                'page_size': '20',
                'types': 'time',
            }
            url = self.commentapi + urlencode(parmas)
            info = requests.get(url, headers=self.headers).json()
            pageNum = int(info['data']['totalCount']/20)+1
            for page in range(1,pageNum+1):
                parmas['page'] = page
                url = self.commentapi+urlencode(parmas)
                yield scrapy.Request(url,callback=self.parse_item,meta={'title':title,'albumurl':response.meta['albumurl'],'episode':episode,'videourl':videourl},dont_filter=False)

    def parse_item(self, response):
        contents = json.loads(response.text)['data']
        if contents['hot']:
            for content in contents['hot']:
                item = MoviecommentsItem()
                item['albumurl'] =response.meta['albumurl']
                item['author'] = content['userInfo']['uname']
                item['comment'] = content['content']
                item['commentId'] =content['id']
                comment_time = content['addTime']
                item['comment_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(comment_time))
                item['ctime'] = str(datetime.now()).split('.')[0]
                item['title'] = response.meta['title']
                item['episode'] = response.meta['episode']
                item['videourl'] = response.meta['videourl']
                item['site'] = 'iqiyi'
                item['ctime'] = str(datetime.now()).split('.')[0]
                yield item
        else:
            for content in contents['comments']:
                item = MoviecommentsItem()
                item['albumurl'] = response.meta['albumurl']
                item['author'] = content['userInfo']['uname']
                item['comment'] = content['content']
                item['commentId'] = content['id']
                comment_time = content['addTime']
                item['comment_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(comment_time))
                item['ctime'] = str(datetime.now())
                item['title'] = response.meta['title']
                item['episode'] = response.meta['episode']
                item['videourl'] =response.meta['videourl']
                item['site'] = 'iqiyi'
                item['ctime'] = str(datetime.now()).split('.')[0]
                if content['content'] != '分享投票':
                    yield item

