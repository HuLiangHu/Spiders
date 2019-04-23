# -*- coding: utf-8 -*-
import scrapy
import json
import re
from douban.items import ReYingMovie
from datetime import datetime


# from scrapy_redis import connection


class ShiguangSpider(scrapy.Spider):

    name = "shiguangmovies"
    start_urls =['http://service.theater.mtime.com/Cinema.api?Ajax_CallBack=true&Ajax_CallBackType=Mtime.Cinema.Services&Ajax_CallBackMethod=CinemaChannelIndexLoadData&Ajax_CrossDomain=1&Ajax_RequestUrl=http%3A%2F%2Ftheater.mtime.com%2FChina_Shanghai%2F&t=201811218322020203&Ajax_CallBackArgument0=232384%2C227422&Ajax_CallBackArgument1=&Ajax_CallBackArgument2=232384%2C251180%2C235060%2C246624%2C209599%2C227422%2C225752%2C257982%2C261009%2C247685%2C261079%2C219640%2C250829%2C253841%2C251866%2C244530%2C258524%2C253766%2C242119%2C247505%2C250539%2C261299%2C224680%2C218216%2C247663%2C260266%2C249650%2C235113%2C260087%2C259796%2C197422%2C236593%2C260741%2C240989%2C10808%2C254620%2C253027%2C231305%2C222531%2C261117%2C103937%2C216920%2C260668%2C261062%2C129119%2C255797%2C233486%2C237072%2C235971%2C253857%2C254854%2C246812%2C261116%2C46846%2C37858%2C48139%2C260061%2C251439%2C205189%2C16083%2C217497%2C236671%2C253823%2C247295&Ajax_CallBackArgument3=260741%2C246812%2C224691%2C253027%2C103937%2C253857%2C235971%2C261062%2C261098%2C237072%2C261116%2C259369%2C260276%2C261331%2C261259%2C251976%2C258677%2C232243%2C250056%2C260719%2C222528%2C237589%2C249748%2C226450%2C256031%2C261273%2C254068%2C260061%2C261310%2C260655%2C261312%2C236588%2C261334%2C235218%2C219170%2C233844%2C253914%2C261214%2C247510%2C132277%2C237903%2C225824%2C259632%2C237366%2C206265%2C261011%2C257510%2C260450%2C253022%2C260666%2C255481%2C234316%2C225751%2C259945%2C254645%2C255770%2C234544%2C210860']
    detail_url='http://service.library.mtime.com/Movie.api?Ajax_CallBack=true&Ajax_CallBackType=Mtime.Library.Services&Ajax_CallBackMethod=GetMovieOverviewRating&Ajax_CrossDomain=1&Ajax_RequestUrl=http%3A%2F%2Fmovie.mtime.com%2F253688%2F&t=20188623322769205&Ajax_CallBackArgument0={}'
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url)

    # def hotplay_requests(self):
    #     url='http://service.theater.mtime.com/Cinema.api?Ajax_CallBack=true&Ajax_CallBackType=Mtime.Cinema.Services&Ajax_CallBackMethod=GetOnlineMoviesInCity&Ajax_CrossDomain=1&Ajax_RequestUrl=http%3A%2F%2Ftheater.mtime.com%2FChina_Shanghai%2F&Ajax_CallBackArgument0=292'
    #     yield scrapy.Request(url,callback=self.parse_grade)
    # # def hotplay_parse(self,response):
    def parse(self, response):
        jsonstr=re.findall('var result_\d+ = (.*);var',response.text)[0]
        item = ReYingMovie()
        for i in json.loads(jsonstr)['value']['hotplayRatingList']:
            item["filmid"]=i['Id']
            url = self.detail_url.format(str(item['filmid']))
            # print(url)
            yield scrapy.Request(url, callback=self.parse_grade)

        for i in json.loads(jsonstr)['value']['upcomingTicketList']:
            item["filmid"] = i['Id']

            url=self.detail_url.format(str(item['filmid']))
            # print(url)
            yield scrapy.Request(url,callback=self.parse_grade)
    # def parse(self, response):
    #     jsonStr = re.search('var hotplaySvList = (\[.*\]);',response.text).group(1)
    #     items = json.loads(jsonStr)
    #
    #     for item in items:
    #         next_url=self.detail_url.format(item['Id'])
    #         yield scrapy.Request(next_url,callback=self.parse_grade)
    #     for url in response.xpath('//dl[@id="upcomingSlide"]/dd/ul/li/a/@href').extract():
    #         id= re.search('movie.mtime.com/(\d+)/',url).group(1)
    #         next_url=self.detail_url.format(id)
    #         yield scrapy.Request(next_url,callback=self.parse_grade)
    #

    def parse_grade(self,response):
        data = json.loads(re.findall(r'({.*})',response.text)[0])
        #print(data)
        #print(data['value']['movieRating']['RatingFinal'])
        item = ReYingMovie()
        item["createdtime"]=str(datetime.now())
        item["comefrom"]="时光"
        item['name']=data['value']['movieTitle']
        item["Grade"] =data['value']['movieRating']["RatingFinal"]
        if item["Grade"]<0:
            item["Grade"]=None
        item["gradePeople"] = data['value']['movieRating']["Usercount"]
        item["want"] = data['value']['movieRating']["AttitudeCount"]
        item["music"] = data['value']['movieRating']["ROtherFinal"]
        item["frames"] = data['value']['movieRating']["RPictureFinal"]
        item["story"] = data['value']['movieRating']["RStoryFinal"]
        item["director"] = data['value']['movieRating']["RDirectorFinal"]
        item["filmid"]=data['value']['movieRating']['MovieId']
        item["crawldate"]=str(datetime.today())
        #print(item)
        return item

