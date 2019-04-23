# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class TiebaStats(scrapy.Item): 
    url = scrapy.Field()
    member_count = scrapy.Field(default=0)
    sign_count = scrapy.Field(default=0)
    post_count = scrapy.Field(default=0)
    thread_count = scrapy.Field(default=0)
    name = scrapy.Field()
    category = scrapy.Field()
    day = scrapy.Field()