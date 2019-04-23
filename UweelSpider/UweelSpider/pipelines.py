# -*- coding: utf-8 -*-
# __author__ = hul
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging

from twisted.enterprise import adbapi

from UweelSpider.items import UweelSpiderItem


class MySqlPipeline(object):
    """A pipeline to store the item in a MySQL database.
    This implementation uses Twisted's asynchronous database API.
    """

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
            use_unicode=True,
            cp_reconnect=True,
        )
        dbpool = adbapi.ConnectionPool('pymysql', **dbargs)
        return cls(dbpool)

    def process_item(self, item, spider):
        # run db query in the thread pool
        if isinstance(item, UweelSpiderItem):
           self.dbpool.runInteraction(self._do_weibo_upsert, item, spider)

    def _do_weibo_upsert(self, conn, item, spider):
        """Perform an insert or update."""
        conn.execute("""insert ignore into `uweel_content` 
        (`wid`,`circleName`,`title`,`content`,`img_url`,`video_cover`,`video_url`,
        `article_type`,`definite_type`,`long_text_cover`,`long_text_summary`,`crawldate`,`circleId`,`resource`)
        values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""",
                     (item['wid'],item['circleName'], item['title'], item['content'],
                      item['img_url'],item['video_cover'] ,item['video_url'],item['article_type']
                      ,item['definite_type'],item['long_text_cover'],item['long_text_summary'],item['crawldate'],
                      item['circleId'],item['resource']))
        logging.info("Item updated in db: %s %r" % (item['title'], item))

    def _handle_error(self, failure, item, spider):
        """Handle occurred on db interaction."""
        # do nothing, just log
        logging.error(failure)

