# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class TVPlayItem(scrapy.Item):
    renqi = scrapy.Field()
    url = scrapy.Field()
    aid = scrapy.Field(default=None)
    guid = scrapy.Field()
    name =  scrapy.Field()
    area = scrapy.Field(default=None)
    desc =  scrapy.Field(default= None)
    episodes =  scrapy.Field(default= None) 
    directors =  scrapy.Field(default= None)
    actors =  scrapy.Field(default= None)
    cover_img =  scrapy.Field(default= None)
    cover_img_sm =  scrapy.Field(default= None)
    playdate = scrapy.Field()
    playCount = scrapy.Field()
    playStatus = scrapy.Field(default= None)
    genre = scrapy.Field(default= None)
    tags = scrapy.Field(default= None)
    lastepisode = scrapy.Field(default= None)
    additional_infos = scrapy.Field(default= {})
    website = scrapy.Field()
    releaseDate = scrapy.Field(default= None)
    alias = scrapy.Field()
    renqi = scrapy.Field()