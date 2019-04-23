# -*- coding: utf-8 -*-
import scrapy
import json
import re
from scrapy.selector import Selector
from douban.items import ReYingMovie
from datetime import datetime
from lxml import etree



# from scrapy_redis import connection


class NuomiMoviesSpider(scrapy.Spider):

    name = "nuomimovies"
    reyinurl = 'https://dianying.nuomi.com/movie/getmovielist?pagelets[]=pageletMovielist&reqID=0&type=hot&cityId=289&pageNum={}&pageSize=10&needMovieNews=false&isHomePage=false&needSliceAdSpace=false&t=1516698958446'
    newurl = 'https://dianying.nuomi.com/movie/getmovielist?pagelets[]=pageletMovielist&reqID=0&type=new&cityId=289&pageNum={}&pageSize=10&needMovieNews=false&isHomePage=false&needSliceAdSpace=false&t=1516698958446'

    def start_requests(self):
        for i in range(0,5):
            url = self.reyinurl.format(i)
            yield scrapy.Request(url,callback=self.parse_grade)
        for i in range(0,5):
            url = self.newurl.format(i)
            yield scrapy.Request(url,callback=self.parse_grade)
        

    def parse_grade(self,response):
        get_data = re.findall(r'({.*})',response.text)[0]
        data = json.loads(get_data)["html"]
        page_source= etree.HTML(data)
        title=page_source.xpath('//a[@class="movie-pic"]/img/@alt')
        grade=page_source.xpath('//span[@class="num nuomi-red"]/text()')
        moviedate=page_source.xpath('///ul[@class="info"]/li[3]/text()')
        movieid=page_source.xpath('//a[@class="movie-pic"]/@data-data')
        for i in range(0,10):
            item = ReYingMovie()
            item["name"]=title[i].strip()
            item["comefrom"]="糯米"
            item["movieDate"]=moviedate[i].strip()[5:]
            item["Grade"]=grade[i].strip()
            item["createdtime"]=str(datetime.now())
            item["filmid"]=re.findall(r"(\d+)",movieid[i])[0]
            item["crawldate"]=str(datetime.today())
            yield item








