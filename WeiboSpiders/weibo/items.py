# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class WeiboIndex(scrapy.Item):
    keyword =scrapy.Field()
    wid = scrapy.Field()
    pc = scrapy.Field(default=0)
    mobile = scrapy.Field(default=0)
    total = scrapy.Field(default=0)
    day = scrapy.Field()
    
class WeiboIndexId(scrapy.Item):
    word = scrapy.Field()
    wid = scrapy.Field()
	
class WeiboStats(scrapy.Item): 
    weiboid = scrapy.Field()
    followers_count = scrapy.Field(default=0)
    friends_count = scrapy.Field(default=0)
    statuses_count = scrapy.Field(default=0)
    day = scrapy.Field()

class BaseItem(scrapy.Item):
    _sys_collection = scrapy.Field()

class WeiboUser(BaseItem): 
     
    id = scrapy.Field()
    _sys_collection = scrapy.Field()
    screen_name = scrapy.Field(default='')
    profile_url = scrapy.Field(default='')
    gender = scrapy.Field(default='n')
    birthday = scrapy.Field()
    statuses_count = scrapy.Field(default = 0)
    created_at = scrapy.Field()
    friends_count = scrapy.Field(default = 0)
    followers_count = scrapy.Field(default = 0)
    verified = scrapy.Field(default = 0)
    vip = scrapy.Field(default = 0)
    tags = scrapy.Field(default = '')
    avatar_large = scrapy.Field(default = '')
    address = scrapy.Field(default = '')
    verified_reason = scrapy.Field(default = '')
    province  = scrapy.Field()
    city  = scrapy.Field()

class WeiboStatus(BaseItem): 
     
    id = scrapy.Field()
    mid = scrapy.Field()
    text = scrapy.Field(default='')
    created_at = scrapy.Field()
    source = scrapy.Field(default='未知')
    reposts_count = scrapy.Field(default = 0)
    comments_count = scrapy.Field(default = 0)
    attitudes_count = scrapy.Field(default = 0)
    thumbnail_pic = scrapy.Field()
    bmiddle_pic = scrapy.Field()
    original_pic  = scrapy.Field()
    pic_ids  = scrapy.Field()
    geo  = scrapy.Field()
    user_id = scrapy.Field()
    
    reposts_status_id = scrapy.Field()