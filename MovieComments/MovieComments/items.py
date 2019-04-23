# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MoviecommentsItem(scrapy.Item):
    # define the fields for your item here like:
    albumurl =scrapy.Field()
    title =scrapy.Field(default=None)
    author = scrapy.Field()
    comment =scrapy.Field()
    comment_time =scrapy.Field()
    site = scrapy.Field()
    episode = scrapy.Field()
    ctime=scrapy.Field()
    videourl=scrapy.Field()
    commentId=scrapy.Field()



