# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class VarietyItem(scrapy.Item):
    url = scrapy.Field()
    aid = scrapy.Field(default=None)
    hashcode = scrapy.Field()
    name =  scrapy.Field()
    area = scrapy.Field(default=None)
    desc =  scrapy.Field(default= None)
    cover_img =  scrapy.Field(default= None)
    playdate = scrapy.Field()
    playCount = scrapy.Field()
    playStatus = scrapy.Field(default= None)
    host = scrapy.Field(default=None) #主持人
    player = scrapy.Field(default=None) #嘉宾
    category = scrapy.Field(default= None)
    tags = scrapy.Field(default= None)
    additional_infos = scrapy.Field(default= {})
    website = scrapy.Field()
    releaseDate = scrapy.Field(default= None) 
    lastseries = scrapy.Field() #最新一集
    tv = scrapy.Field(default=None)  #电视台 
    
class VarietyVideoItem(scrapy.Item): #当集视频
    url = scrapy.Field()
    aid = scrapy.Field(default=None)
    vid = scrapy.Field(default=None)
    hashcode = scrapy.Field(default = None)
    albumurl = scrapy.Field()
    albumnhashcode = scrapy.Field()
    playdate = scrapy.Field()
    playCount = scrapy.Field()
    video_img =  scrapy.Field(default= None)
    name  = scrapy.Field()
    desc = scrapy.Field(default= None) 
    player = scrapy.Field(default=None) #嘉宾
    releaseDate = scrapy.Field(default= None) 
    additional_infos = scrapy.Field(default= {})
    website = scrapy.Field()
    duration = scrapy.Field(default = None)
    episode = scrapy.Field(default = None)
	
    