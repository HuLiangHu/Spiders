# -*- coding: utf-8 -*-
import scrapy
import json
import re
from scrapy.selector import Selector
from douban.items import ReYingMovie
from datetime import datetime


# from scrapy_redis import connection


class XinlangMoviesSpider(scrapy.Spider):

    name = "sinamovies"
    reyinurls = ['http://movie.weibo.com/movie/web/ajax_getRankTaobao?date=&data_type=movie_hot_day_poll']
    futureurl=['http://movie.weibo.com/movie/web/ajax_getRankTaobao?date=&data_type=movie_will_day_poll']

    def start_requests(self):
        # self.server = connection.from_settings(self.settings)
        for url in self.reyinurls:
            yield scrapy.Request(url,callback=self.parse_grade)
        for url in self.futureurl:
            yield scrapy.Request(url,callback=self.parse_futuregrade)




    def parse_grade(self,response):
        data = json.loads(response.text)
        for i in data["content"]:
            item = ReYingMovie()
            item["name"]=i["trendinfo"]["name"]
            item["createdtime"]=str(datetime.now())
            item["movieDate"]=i["release_date"]
            item["want"] = i["want_number"]
            item["comefrom"]="微博"
            item["filmid"]=i["film_id"]
            item["crawldate"]=str(datetime.today())
            item["Grade"]=i["markinfo"]["score"]
            item["gradePeople"]=i["markinfo"]["score_count"]
            item["good"]=format(i["markinfo"]["good_rate"],'.0%')
            item["bad"]=format(i["markinfo"]["bad_rate"],'.0%')
            yield item


    def parse_futuregrade(self,response):
        data = json.loads(response.text)

        for i in data["content"]:
            item = ReYingMovie()
            item["name"]=i["name"]
            item["comefrom"]="微博"
            item["filmid"] = i["film_id"]
            item["crawldate"] = str(datetime.today())
            item["createdtime"]=str(datetime.now())
            item["movieDate"]=i["release_time"]
            item["want"]=i["want_number"]
            yield item






