# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
from twisted.enterprise import adbapi
from datetime import datetime
import pymysql
import pymysql.cursors
from scrapy import signals
import logging
from Maoyan.items import *
#import pymongo

#class MongoPipeline(object):


class MaoyanPipeline(object):

    def __init__(self):
        self.film = codecs.open('tvs_data.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.film.write(line)
        return item

    def spider_closed(self, spider):
        self.film.close()


class MySqlPipeline(object):

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True,
            cp_reconnect=True,
        )
        dbpool = adbapi.ConnectionPool('pymysql', **dbargs)
        return cls(dbpool)

    # pipeline默认调用
    def process_item(self, item, spider):
        if isinstance(item, DailyBoxOfficeItem):
            d = self.dbpool.runInteraction(self._do_dailyboxoffice_upsert, item, spider) 
        if isinstance(item, MaoyanItem):
            d = self.dbpool.runInteraction(self._do_upinsert, item, spider)
        if isinstance(item, BoxofficeItem):
            d = self.dbpool.runInteraction(
                self._do_boxoffice_upinsert, item, spider)
        if isinstance(item, exclusiveieceItem):
            d = self.dbpool.runInteraction(
                self._do_exclusivepiece_upinsert, item, spider)
        if isinstance(item, CityItem):
            d = self.dbpool.runInteraction(
                self._do_city_upinsert, item, spider)
        if isinstance(item, FilmcastItem):
            d = self.dbpool.runInteraction(
                self._do_filmcast_upinsert, item, spider)
        if isinstance(item, AudiencesItem):
            d = self.dbpool.runInteraction(
                self._do_audiences_upinsert, item, spider)
        if isinstance(item, ExpectItem):
            d = self.dbpool.runInteraction(
                self._do_exp_upinsert, item, spider)
        # d = self.dbpool.runInteraction(self._do_upinsert, item, spider)
        d.addErrback(self._handle_error, item, spider)
        d.addBoth(lambda _: item)
        return d

        # 将每行更新或写入数据库中
    def _do_dailyboxoffice_upsert(self,conn,item,spider):
        try:
            conn.execute("""
                                insert ignore INTO `rawdata_movie_dailyboxoffice_maoyan`
                                            (`day`,`maoyanid`,`name`,`showDay`,`summaryBoxOffice`,`totalBoxOffice`,`dailyBoxOffice`,`boxofficePer`,`screeningsPer`,`attendance`)
                                            VALUES
                                            (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                            """, (
                item['day'], item['maoyanid'], item['name'], item['showDay'],
                item['summaryBoxOffice'], item['totalBoxOffice'], item['dailyBoxOffice'], item['boxofficePer'], item['screeningsPer'], item['attendance']))
        except Exception as e:
            print(item)
            print('*'*100)
            print(e)
        logging.info("Item insert in db: %r" % (item))
    def _do_upinsert(self, conn, item, spider):
        now = datetime.utcnow().replace(microsecond=0).isoformat(' ')

        conn.execute("""
                            replace INTO `movie_rawdata_basicinfo`
                                        (`name`,
                                        `url`,
                                        `filmid`,
                                        `wish`,
                                        `image`,
                                        `publishdate`,
                                        `version`,
                                        `duration`,
                                        `score`,
                                        `category`,
                                        `director`,
                                        `actors`,
                                        `productionCompany`,
                                        `distributionFirm`,
                                        `description`,
                                        `totalBoxOffice`,
                                        `filmDayBoxOffice`,
                                        `firstweekBoxOffice`,
                                        `crawldate`
                                        )
                                        VALUES
                                        (%s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s)
                        """, (
            item['name'], item['url'], item['filmid'], item[
                'wish'], item['image'], item['publishdate'],
            item['version'], item['duration'], item[
                'score'], item['category'], item['director'],
            item['actors'], item['productionCompany'], item['distributionFirm'],
            item['description'], item[
                'totalBoxOffice'], item['filmDayBoxOffice'],
            item['firstweekBoxOffice'], now))
        logging.info("Item insert in db: %r" % (item))

    def _do_boxoffice_upinsert(self, conn, item, spider): 

        conn.execute("""
                            replace INTO `movie_rawdata_dailyboxoffice`
                                        (`filmid`,
                                        `day`,
                                        `boxOffice`,
                                        `boxOfficePercent`,
                                        `exclusivePiecePercent`,
                                        `personAmount`,`crawldate`)
                                        VALUES
                                        (%s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s )
                        """, (
            item['filmid'], item['day'], item['boxOffice'], item['boxOfficePercent'],
            item['exclusivePiecePercent'], item['personAmount'],str(datetime.today())))
        logging.info("Item insert in db: %r" % (item))

    def _do_exclusivepiece_upinsert(self, conn, item, spider):
        now = datetime.utcnow().replace(microsecond=0).isoformat(' ')

        conn.execute("""
                            replace INTO `movie_rawdata_exclusivepiece`
                                        (`filmid`,
                                        `filmDay`,
                                        `day`,
                                        `filmTimes`,
                                        `exclusivePiecePercent`,
                                        `seats`,
                                        `seatsPercent`,
                                        `goldFieldPercent`,
                                        `crawldate`)
                                        VALUES
                                        (%s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s)
                        """, (
            item['filmid'], item['filmDay'], item['day'], item[
                'filmTimes'], item['exclusivePiecePercent'],
            item['seats'], item['seatsPercent'], item['goldFieldPercent'], now))
        logging.info("Item insert in db: %r" % (item))

    def _do_city_upinsert(self, conn, item, spider): 
        try:
            conn.execute("""
                                replace INTO `movie_rawdata_city`
                                            (`filmid`,
                                            `day`,
                                            `city`,
                                            `boxOffice`,
                                            `boxOfficePercent`,
                                            `exclusivePiecePercent`,
                                            `boxOfficeAmount`,
                                            `seatsPercent`,
                                            `goldFieldPercent`,
                                            `personAmount`,
                                            `person`,
                                            `filmTimes`)
                                            VALUES
                                            (%s,
                                            %s,
                                            %s,
                                            %s,
                                            %s,
                                            %s,
                                            %s,
                                            %s,
                                            %s,
                                            %s,
                                            %s,
                                            %s )
                            """, (
                item['filmid'], item['day'], item['city'], item[
                    'boxOffice'], item['boxOfficePercent'],
                item['exclusivePiecePercent'], item['boxOfficeAmount'], item[
                    'seatsPercent'], item['goldFieldPercent'],
                item['personAmount'], item['person'], item['filmTimes']))
            logging.info("Item insert in db: %r" % (item))
        except Exception as e:
            print(e)

    def _do_filmcast_upinsert(self, conn, item, spider):
        now = datetime.utcnow().replace(microsecond=0).isoformat(' ')

        conn.execute("""
                            replace INTO `movie_rawdata_filmcast`
                                        (`filmid`,
                                        `day`,
                                        `filmcast`,
                                        `boxOffice`,
                                        `boxOfficePercent`,
                                        `exclusivePiecePercent`,
                                        `boxOfficeAmount`,
                                        `seatsPercent`,
                                        `goldFieldPercent`,
                                        `personAmount`,
                                        `person`,
                                        `filmTimes`,
                                        `crawldate`)
                                        VALUES
                                        (%s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s)
                        """, (
            item['filmid'], item['day'], item['filmcast'], item[
                'boxOffice'], item['boxOfficePercent'],
            item['exclusivePiecePercent'], item['boxOfficeAmount'], item[
                'seatsPercent'], item['goldFieldPercent'],
            item['personAmount'], item['person'], item['filmTimes'], now))
        logging.info("Item insert in db: %r" % (item))

    def _do_audiences_upinsert(self, conn, item, spider):
        now = datetime.utcnow().replace(microsecond=0).isoformat(' ') 
        try:
              
            conn.execute("""
                                replace INTO `movie_rawdata_audiences`
                                            (`filmid`,
                                            `male`,
                                            `female`,
                                            `crawldate`,
                                            `agegroup1`,
                                            `agegroup2`,
                                            `agegroup3`,
                                            `agegroup4`,
                                            `agegroup5`,
                                            `agegroup6`)
                                            VALUES
                                            (%s,
                                            %s,
                                            %s,
                                            %s,
                                            %s,
                                            %s,
                                            %s,
                                            %s,
                                            %s,
                                            %s)
                            """, (
                item['filmid'], item['male'], item['female'], now, item['agegroup1'], 
                item['agegroup2'], item['agegroup3'], item['agegroup4'], item['agegroup5'],
                item['agegroup6']))
        except Exception as e: 
            logging.info("*" * 100) 
        logging.info("Item insert in db: %r" % (item))

    def _do_exp_upinsert(self, conn, item, spider):
        now = datetime.utcnow().replace(microsecond=0).isoformat(' ')

        conn.execute("""
                            replace INTO `movie_rawdata_exp`
                                        (`filmid`,
                                        `cityOrder`,
                                        `city`,
                                        `exp`,
                                        `crawldate`)
                                        VALUES
                                        (%s,
                                        %s,
                                        %s,
                                        %s,
                                        %s)
                        """, (
            item['filmid'], item['cityOrder'], item['city'], item[
                'exp'], now))
        logging.info("Item insert in db: %r" % (item))

    # 异常处理

    def _handle_error(self, failue, item, spider):
        print('$'*100)
        logging.err(failue)
