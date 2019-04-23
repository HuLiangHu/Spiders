# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class DoubanMovieGrade(scrapy.Item):
    name = scrapy.Field()
    createdtime=scrapy.Field()
    movieDate = scrapy.Field(default=None)
    doubanGrade = scrapy.Field(default=0)
    gradePeople = scrapy.Field(default=0)
    five = scrapy.Field(default=0)
    four = scrapy.Field(default=0)
    three = scrapy.Field(default=0)
    two = scrapy.Field(default=0)
    one = scrapy.Field(default=0)




    
    