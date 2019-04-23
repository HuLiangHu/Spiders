# -*- coding: utf-8 -*-
import scrapy
import json
import re
from scrapy.selector import Selector
import random
from datetime import datetime
from scrapy.utils.project import get_project_settings
import pymysql
from scrapy.http import HtmlResponse
import random
from douban.items import DoubanMovieGrade
from datetime import datetime


# from scrapy_redis import connection


class DoubanMoviesSpider(scrapy.Spider):

    name = "reyinmovies"
    start_urls = ['https://movie.douban.com/cinema/nowplaying/shanghai/']

    def start_requests(self):
        # self.server = connection.from_settings(self.settings)

        for url in self.start_urls:
            yield scrapy.Request(url)

    def parse(self, response):
        detail_urls = response.xpath('//*[@id="nowplaying"]/div[2]/ul/li/ul/li[@class="stitle"]/a[@href]/@href').extract()
        print(detail_urls)
        for url in detail_urls:
            yield scrapy.Request(url,callback=self.parse_grade)


    def parse_grade(self,response):
        selector = Selector(response)
        item = DoubanMovieGrade()
        item["name"]=selector.xpath('//span[@property="v:itemreviewed"]/text()').extract_first()
        item["createdtime"]=str(datetime.now())
        try:
            item["movieDate"]=selector.xpath('//span[@property="v:initialReleaseDate"]/text()').extract_first()
            item["doubanGrade"] = selector.xpath('//strong[@property]/text()').extract_first()
            item["gradePeople"] = selector.xpath('//span[@property="v:votes"]/text()').extract_first()
            rating = selector.xpath('//span[@class="rating_per"]/text()').extract()
            item["five"] = rating[0]
            item["four"] = rating[1]
            item["three"] = rating[2]
            item["two"] = rating[3]
            item["one"] = rating[4]
        except IndexError:
            item["movieDate"]="暂无"
            item["doubanGrade"] = "暂无"
            item["gradePeople"] = "暂无"
            item["five"] = "暂无"
            item["four"] = "暂无"
            item["three"] = "暂无"
            item["two"] = "暂无"
            item["one"] = "暂无"



        return item

