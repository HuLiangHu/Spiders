# -*- coding: utf-8 -*-
# __author__ = hul
# __date__ = 2018/10/23 下午9:10
import requests
from urllib.parse import urlencode
import scrapy
import re
import json
import time
import zlib
import random
from datetime import datetime

class DMiqiyiSpider(scrapy.Spider):
    name = 'DMiqiyi'
    # 视频详情页
    start_url= 'https://www.iqiyi.com/v_19rsjeyhq4.html'#视频详情页url
    base_url = 'http://mixer.video.iqiyi.com/jp/mixin/videos/{id}'
    danmu_url = 'http://cmts.iqiyi.com/bullet/%s/%s/%s_300_%s.z?rn=%s&business=danmu&is_iqiyi=true&is_video_page=true&tvid=%s&albumid=%s&categoryid=%s&qypid=01010021010000000000'
#############
    ##电视剧
    def start_requests(self):

        yield scrapy.Request(self.start_url,callback=self.parse_albumId)
##############

#############
    # ###综艺
    # def start_requests(self):
    #     yield scrapy.Request(self.start_url, callback=self.parse_zongyi_danmu)

############
    def parse_albumId(self,response):
        """

        :param response:
        :return:获取电视的albumId
        """
        albumId = re.search('albumId: \"(\d+)\"',response.text).group(1)
        url='https://pcw-api.iqiyi.com/albums/album/avlistinfo?aid={}&page=1&size=100'.format(albumId)
        yield scrapy.Request(url, callback=self.parse_danmu,meta={"albumId":albumId})

    def parse_danmu(self,response):

        for info in json.loads(response.text)['data']['epsodelist']:
            #print(info)
            albumId ='226444301'
            title = info['name']
            tvid = info['tvId']
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
            }
            duration = info['duration'].split(':')[0]
            danmuList = []
            page = int(duration)
            for i in range(1, page + 1):
                # print(i, '*' * 20)
                try:
                    t = '0000' + str(tvid)
                    length = len(t)
                    first = t[length - 4:length - 2]
                    second = t[length - 2:]
                    rn = '0.' + self.randomNumer(16)
                    url = self.danmu_url % (first, second, tvid, i, rn, tvid, albumId,2)
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
                    }
                    response = requests.get(url, headers=headers)

                    danmuList.append(zlib.decompress(response.content).decode('utf-8'))



                    content = danmuList[i - 1]
                    comments = re.findall('<content>(.*?)</content>', content)
                    # authors =re.findall(' <name>(.*?)</name>',content)
                    showtimes = re.findall('<showTime>(.*?)</showTime>', content)
                    item = {}
                    for comment, showtime in zip(comments, showtimes):
                        item['comment'] = comment
                        item['showtime'] = str(int(int(showtime) / 60)) + '分' + str(int(int(showtime) % 60)) + '秒'
                        item['title'] = title
                        yield item
                except:
                    pass

    def parse_zongyi_danmu(self, response):
        tvid = re.search('\[\'tvid\'\] = \"(\d+)\"', response.text).group(1)
        albumId = re.search('\[\'albumId\'\] = \"(\d+)\"', response.text).group(1)
        title =response.xpath('//meta[@property="og:title"]/@content').extract_first()
        danmuList = []
        duration = self.get_zongyi_duration(tvid)
        page = int(duration) #片长多少分钟
        for i in range(1, page + 1):
            try:
                t = '0000' + str(tvid)
                length = len(t)
                first = t[length - 4:length - 2]
                second = t[length - 2:]
                rn = '0.' + self.randomNumer(16)
                url = self.danmu_url % (first, second, tvid, i, rn, tvid, albumId, 2)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
                }
                response = requests.get(url, headers=headers)

                danmuList.append(zlib.decompress(response.content).decode('utf-8'))

                content = danmuList[i - 1]
                comments = re.findall('<content>(.*?)</content>', content)
                # authors =re.findall(' <name>(.*?)</name>',content)
                showtimes = re.findall('<showTime>(.*?)</showTime>', content)
                item = {}
                for comment, showtime in zip(comments, showtimes):
                    item['comment'] = comment
                    item['showtime'] = str(int(int(showtime) / 60)) + '分' + str(int(int(showtime) % 60)) + '秒'
                    item['title'] = title
                    yield item
            except:
                pass
    def randomNumer(self,n):
        result = ""
        for i in range(n):
            result += str(random.choice(range(10)))
        return result

    def get_zongyi_duration(self,tvid):
        res = requests.get('https://static-lvjing.iqiyi.com/lvjing/0/2/{}.json?'.format(tvid))
        return len(json.loads(res.text)['value'])/60 #得到总时长为分钟