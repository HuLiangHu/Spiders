# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MoviecountsItem(scrapy.Item):
    title=scrapy.Field()
    view_count=scrapy.Field()
    comefrom=scrapy.Field()
    datetime=scrapy.Field()
    url=scrapy.Field()
    updatetime=scrapy.Field()


