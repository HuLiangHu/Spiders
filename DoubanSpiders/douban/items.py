# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class DoubanMovieInfo(scrapy.Item): 
    id = scrapy.Field()
    rating = scrapy.Field(default=0)
    ratings_count = scrapy.Field(default=0)
    comments_count = scrapy.Field(default=0)
    reviews_count = scrapy.Field(default=0)
    wish_count = scrapy.Field(default=0)
    collect_count = scrapy.Field(default=0)
    year = scrapy.Field(default=None)
    image = scrapy.Field(default=None) 
    genres = scrapy.Field(default=None)
    countries = scrapy.Field(default=None)
    casts = scrapy.Field(default=None)
    episodes_count = scrapy.Field(default = None)
    title = scrapy.Field()
    type = scrapy.Field()
    duration =scrapy.Field()
    original_title = scrapy.Field(default = None)
    directors = scrapy.Field(default=None)
    aka = scrapy.Field(default=None) 
    _sys_collection = scrapy.Field(default='douban_movieinfo')
    
    