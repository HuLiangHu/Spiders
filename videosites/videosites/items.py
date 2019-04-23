# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AlbumnItem(scrapy.Item):
    url = scrapy.Field()
    id = scrapy.Field()
    type = scrapy.Field() # movie,tv,variety
    hash = scrapy.Field()
    aid = scrapy.Field(default=None) 
    name =  scrapy.Field() #中文名、默认名称，必填
    name_en = scrapy.Field() #英文名
    series_name = scrapy.Field() #系列名称
    series_num = scrapy.Field() #系列数
    area = scrapy.Field(default=None)
    desc =  scrapy.Field(default= None)
    episodes =  scrapy.Field(default= None) 
    directors =  scrapy.Field(default= None)
    actors =  scrapy.Field(default= None)
    cover_img =  scrapy.Field(default= None)
    cover_img_sm =  scrapy.Field(default= None)
    playStatus = scrapy.Field(default= None)
    genre = scrapy.Field(default= None)
    tags = scrapy.Field(default= None)
    lastepisode = scrapy.Field(default= None)
    additional_infos = scrapy.Field(default= {})
    website = scrapy.Field()
    releaseDate = scrapy.Field(default= None)
    alias = scrapy.Field()
