# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class KKItem(scrapy.Item):
    url = scrapy.Field()
    site = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    animeid = scrapy.Field()
    status = scrapy.Field()
    click_count = scrapy.Field()#热度
    comment_count = scrapy.Field()
    comics_count = scrapy.Field()#章节数
    tags = scrapy.Field()
    category = scrapy.Field()
    renqi = scrapy.Field()
    likes = scrapy.Field() #点赞
    coll_count = scrapy.Field() #关注
class GcrspidersItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class MkItem(scrapy.Item):
    url = scrapy.Field()
    site = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    animeid = scrapy.Field()
    status = scrapy.Field()
    click_count = scrapy.Field()
    comment_count = scrapy.Field()
    recomment_count = scrapy.Field()
    tags = scrapy.Field()
    category = scrapy.Field()
    license_status = scrapy.Field()
    rating = scrapy.Field()
    rating_count = scrapy.Field()
    coll_count = scrapy.Field() #收藏


class U17Item(scrapy.Item):
    url = scrapy.Field()
    site = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    animeid = scrapy.Field()
    status = scrapy.Field()
    click_count = scrapy.Field()
    comment_count = scrapy.Field()
    recomment_count = scrapy.Field()
    tags = scrapy.Field()
    category = scrapy.Field()
    license_status = scrapy.Field()
    monthtickets = scrapy.Field()
    coll_count = scrapy.Field()
    tucao_count = scrapy.Field()

class TxdmItem(scrapy.Item):
    url = scrapy.Field()
    site = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    animeid = scrapy.Field()
    status = scrapy.Field()
    click_count = scrapy.Field()
    comment_count = scrapy.Field()
    tags = scrapy.Field()
    rating = scrapy.Field()
    rating_count = scrapy.Field()
    coll_count = scrapy.Field()
    tucao_count = scrapy.Field()
    redtickets = scrapy.Field()
    blacktickets = scrapy.Field()

class ZztbItem(scrapy.Item):
    indexid = scrapy.Field()
    r4_zztb_vip_number = scrapy.Field()
    r4_zztb_themes_number = scrapy.Field()
    r4_zztb_reply_number = scrapy.Field()

class ZptbItem(scrapy.Item):
    indexid = scrapy.Field()
    r4_zptb_vip_number = scrapy.Field()
    r4_zptb_themes_number = scrapy.Field()
    r4_zptb_reply_number = scrapy.Field()

class DoubanItem(scrapy.Item):
    indexid = scrapy.Field()
    r4_db_reviews_number = scrapy.Field()

class WeiboItem(scrapy.Item):
    indexid = scrapy.Field()
    r3_wb_fans_number = scrapy.Field()
