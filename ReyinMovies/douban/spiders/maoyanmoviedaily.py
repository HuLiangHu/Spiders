# -*- coding: utf-8 -*-
import scrapy
import json
import re
from datetime import datetime
import time
class MaoyanmoviedailySpider(scrapy.Spider):
    name = 'maoyanmoviedaily'
    # allowed_domains = ['maoyan.com']
    # start_urls = ['http://maoyan.com/']
    movieid = '249342'
    now = int(time.time())
    end = now - 60 * 24 * 60 * 60
    startDate =time.strftime('%Y-%m-%d', time.localtime(end))
    endDate =time.strftime('%Y-%m-%d', time.localtime(now))
    startDate = ''.join(startDate.split('-'))
    endDate = ''.join(endDate.split('-'))

    start_urls = ['http://maoyan.com/films?showType=1',  # 正在热映
                  'http://maoyan.com/films?showType=2']  # 即将上映

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.pare_movielist)

    def pare_movielist(self, response):
        movie_links = response.xpath('//div[@class="movie-item"]/a/@href').extract()
        for link in movie_links:
            movieid = re.search('(\d+)',link).group(1)
            url = 'https://piaofang.maoyan.com/movie/{0}/wantchart?startDate={1}&endDate={2}'.format(
                    movieid,self.startDate,self.endDate
                )

            # print(url)
            yield scrapy.Request(url, callback=self.parse_detail)
            next_url = response.xpath("//li/a[text()='下一页']/@href").extract_first()

            if next_url is not None:
                next_url = 'http://maoyan.com/films' + str(next_url)
                # print("下一页的链接:", next_url)
                yield scrapy.Request(next_url, callback=self.pare_movielist)

    # def start_requests(self):
    #     url = 'https://piaofang.maoyan.com/movie/{0}/wantchart?startDate={1}&endDate={2}'.format(
    #         self.movieid,self.startDate,self.endDate
    #     )
    #     yield scrapy.Request(url)
    def parse_detail(self, response):
        info = json.loads(response.text)['wishChart']

        contents = re.findall('data-info="(.*?)想.*?"',info,re.S)

        item={}
        for content in contents:
            item['moviename'] =re.search('《(.*?)》',response.text).group(1)
            item['data'] = content.split(' ')[0]
            item['weekly'] =content.split(' ')[1]
            item['newlyincreasedPeople'] = re.search('(\d+)',content.split(' ')[2]).group(1)
            item["crawldate"] = str(datetime.today())
            print(item)