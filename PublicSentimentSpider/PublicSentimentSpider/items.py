# -*- coding: utf-8 -*-
# __author__ = hul
# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PublicsentimentspiderItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    link = scrapy.Field()
    pubtime = scrapy.Field()
    reply = scrapy.Field()
    content =scrapy.Field()
    crawldate = scrapy.Field()

class Weibo_youwei(scrapy.Item):
    # define the fields for your item here like:
    circleName = scrapy.Field()
    circleId = scrapy.Field()
    resource = scrapy.Field()
    wid = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    img_url = scrapy.Field()
    video_duration =scrapy.Field()
    video_url = scrapy.Field()
    video_cover = scrapy.Field()
    article_type = scrapy.Field()
    definite_type = scrapy.Field()
    long_text_cover =scrapy.Field(default=None)
    long_text_summary=scrapy.Field(default=None)
    crawldate = scrapy.Field()

