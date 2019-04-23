# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class MovieItem(scrapy.Item):
    url = scrapy.Field()
    aid = scrapy.Field(default=None)
    urlhash = scrapy.Field()
    name =  scrapy.Field()
    area = scrapy.Field(default=None)
    desc =  scrapy.Field(default= None)
    directors =  scrapy.Field(default= None)
    actors =  scrapy.Field(default= None)
    cover_img =  scrapy.Field(default= None)
    cover_img_sm =  scrapy.Field(default= None)
    playdate = scrapy.Field()
    playCount = scrapy.Field()
    playStatus = scrapy.Field(default= None)
    genre = scrapy.Field(default= None)
    tags = scrapy.Field(default= None)
    additional_infos = scrapy.Field(default= {})
    website = scrapy.Field()
    releaseDate = scrapy.Field(default= None)
    douban = scrapy.Field(default = None)
    rating = scrapy.Field(default = None)
    alias = scrapy.Field()
    commentcount = scrapy.Field(default =None)
    timeLength = scrapy.Field(default =None)