# -*- coding: utf-8 -*-
import scrapy
import json
import re
from scrapy.selector import Selector
from douban.items import ReYingMovie
from datetime import datetime


# from scrapy_redis import connection


class GewalaMoviesSpider(scrapy.Spider):

    name = "gewalamovies"
    reyinurls = ['http://www.gewara.com/movie/searchMovie.xhtml']
    futureurl='http://www.gewara.com/movie/futureMovie.xhtml?pageNo={}'

    def start_requests(self):
        # self.server = connection.from_settings(self.settings)
        for url in self.reyinurls:
            yield scrapy.Request(url)

        for i in range(0,6):
            url = self.futureurl.format(i)
            yield scrapy.Request(url,callback=self.parse_future)


    def parse(self, response):
        detail_urls = response.xpath('//h2/a/@href').extract()
        for url in detail_urls:
            nexturl='http://www.gewara.com/'+url
            yield scrapy.Request(nexturl,callback=self.parse_grade)


    def parse_grade(self,response):
        selector = Selector(response)
        item = ReYingMovie()
        item["name"]=selector.xpath('//h1/text()').extract_first()
        item["createdtime"]=str(datetime.now())
        item["comefrom"]="格瓦拉"
        item["filmid"]=re.findall(r'\d+',response.url)[0]
        item["crawldate"]=str(datetime.today())
        try:
            item["movieDate"]=selector.xpath('//div[@id="ui_movieInfo_open"]/div/ul/li[@class="first"]/text()').extract_first()[5:]
            item["Grade"] = selector.xpath('//span[@class="point"]/text()').extract_first()
            item["gradePeople"] = selector.xpath('//span[@class="txt"]/em/text()').extract_first()[2:-1]
            rating = selector.xpath('//span[@class="pect"]/text()').extract()
            item["five"] = rating[0][1:-1]
            item["four"] = rating[1][1:-1]
            item["three"] = rating[2][1:-1]
            item["two"] = rating[3][1:-1]
            item["one"] = rating[4][1:-1]
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


    def parse_future(self,response):
        detail_urls = response.xpath('//h2/a/@href').extract()

        for url in detail_urls:
            nexturl='http://www.gewara.com/'+url
            yield scrapy.Request(nexturl,callback=self.parse_futuregrade)

    def parse_futuregrade(self,response):
        item = ReYingMovie()
        item["name"]=response.xpath('//h1/text()').extract_first()
        item["createdtime"]=str(datetime.now())
        item["comefrom"]="格瓦拉"
        item["filmid"] = re.findall(r'\d+', response.url)[0]
        item["crawldate"] = str(datetime.today())
        movieDate = response.xpath('//div[@id="ui_movieInfo_open"]/div/ul/li[@class="first"]/text()').extract_first()
        print(movieDate)
        if movieDate ==None:
            movieDate=response.xpath('//div[@class="toggleInfo clear"]/span[2]/text()').extract_first()
        if movieDate ==None:
            movieDate=response.xpath('//div[@class="toggleInfo clear"]/span[3]/text()').extract_first()
        item["movieDate"]=movieDate[5:]
        item["want"]=response.xpath('//span[@class="focusCount"]/text()').extract_first()[:-2]

        return item





