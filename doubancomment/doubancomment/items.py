# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubancommentItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    author = scrapy.Field()
    comment_time = scrapy.Field()
    comment = scrapy.Field()
    movieId= scrapy.Field()
    commentId =scrapy.Field()
    authorId= scrapy.Field()
    votes = scrapy.Field()
    grade = scrapy.Field()
    ctime = scrapy.Field()

