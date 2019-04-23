# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MaoyanItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(default=None)  # 电影名
    url = scrapy.Field(default=None)  # 电影链接
    filmid = scrapy.Field(default=None)  # 电影ID
    category = scrapy.Field(default=None)  # 电影类别
    score = scrapy.Field(default=None)  # 电影评分
    wish = scrapy.Field(default=None)  # 想看
    description = scrapy.Field(default=None)  # 电影描述
    duration = scrapy.Field(default=None)  # 电影时长
    version = scrapy.Field(default=None)  # 电影版本（2D/3D）
    publishdate = scrapy.Field(default=None)  # 上映日期
    totalBoxOffice = scrapy.Field(default=None)  # 总票房
    filmDayBoxOffice = scrapy.Field(default=None)  # 点映票房
    firstweekBoxOffice = scrapy.Field(default=None)  # 首周票房
    image = scrapy.Field(default=None)  # 电影海报
    site = scrapy.Field(default=None)  # 站点
    director = scrapy.Field(default=None)  # 导演
    actors = scrapy.Field(default=None)  # 主演们
    productionCompany = scrapy.Field(default=None)  # 出品公司
    distributionFirm = scrapy.Field(default=None)  # 发行公司


class BoxofficeItem(scrapy.Item):
    filmid = scrapy.Field(default=None)  # 电影ID
    day = scrapy.Field(default=None)  # 日期
    boxOffice = scrapy.Field(default=None)  # 当日票房
    boxOfficePercent = scrapy.Field(default=None)  # 票房占比
    exclusivePiecePercent = scrapy.Field(default=None)  # 排片占比
    personAmount = scrapy.Field(default=None)  # 场均人次


class exclusiveieceItem(scrapy.Item):
    filmid = scrapy.Field(default=None)  # 电影ID
    day = scrapy.Field(default=None)  # 日期
    filmDay = scrapy.Field(default=None)  # 点映日
    filmTimes = scrapy.Field(default=None)  # 场次
    seats = scrapy.Field(default=None)  # 座位
    exclusivePiecePercent = scrapy.Field(default=None)  # 排片占比
    seatsPercent = scrapy.Field(default=None)  # 排座占比
    goldFieldPercent = scrapy.Field(default=None)  # 黄金场占比
    # crawldate=scrapy.Field(default=None)#爬网日期


class CityItem(scrapy.Item):
    filmid = scrapy.Field(default=None)  # 电影ID
    day = scrapy.Field(default=None)  # 日期
    city = scrapy.Field(default=None)  # 城市
    boxOffice = scrapy.Field(default=None)  # 当日票房
    boxOfficePercent = scrapy.Field(default=None)  # 票房占比
    exclusivePiecePercent = scrapy.Field(default=None)  # 排片占比
    boxOfficeAmount = scrapy.Field(default=None)  # 累计票房
    seatsPercent = scrapy.Field(default=None)  # 排座占比
    goldFieldPercent = scrapy.Field(default=None)  # 黄金场占比
    personAmount = scrapy.Field(default=None)  # 场均人次
    person = scrapy.Field(default=None)  # 人次
    filmTimes = scrapy.Field(default=None)  # 场次


class FilmcastItem(scrapy.Item):
    filmid = scrapy.Field(default=None)  # 电影ID
    day = scrapy.Field(default=None)  # 日期
    filmcast = scrapy.Field(default=None)  # 影投
    boxOffice = scrapy.Field(default=None)  # 当日票房
    boxOfficePercent = scrapy.Field(default=None)  # 票房占比
    exclusivePiecePercent = scrapy.Field(default=None)  # 排片占比
    boxOfficeAmount = scrapy.Field(default=None)  # 累计票房
    seatsPercent = scrapy.Field(default=None)  # 排座占比
    goldFieldPercent = scrapy.Field(default=None)  # 黄金场占比
    personAmount = scrapy.Field(default=None)  # 场均人次
    person = scrapy.Field(default=None)  # 人次
    filmTimes = scrapy.Field(default=None)  # 场次


class AudiencesItem(scrapy.Item):
    filmid = scrapy.Field(default=None)  # 电影ID
    male = scrapy.Field(default=None)  # 男性占比
    female = scrapy.Field(default=None)  # 女性占比
    agegroup1 = scrapy.Field(default = None)
    agegroup2 = scrapy.Field(default = None)
    agegroup3 = scrapy.Field(default = None)
    agegroup4 = scrapy.Field(default = None)
    agegroup5 = scrapy.Field(default = None)
    agegroup6 = scrapy.Field(default = None)
    agegroup7 = scrapy.Field(default = None)


class ExpectItem(scrapy.Item):
    filmid = scrapy.Field(default=None)  # 电影ID
    cityOrder = scrapy.Field(default=None)  # 城市排名
    city = scrapy.Field(default=None)  # 城市
    exp = scrapy.Field(default=None)  # 分数

class DailyBoxOfficeItem(scrapy.Item):
    day = scrapy.Field(default=None)
    maoyanid = scrapy.Field(default=None)
    name = scrapy.Field(default=None)
    showDay = scrapy.Field(default=None)
    summaryBoxOffice = scrapy.Field(default=None)
    totalBoxOffice = scrapy.Field(default=None)
    dailyBoxOffice = scrapy.Field(default=None)
    boxofficePer = scrapy.Field(default=None)
    screeningsPer = scrapy.Field(default=None)
    attendance = scrapy.Field(default=None)