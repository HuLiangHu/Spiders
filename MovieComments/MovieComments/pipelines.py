# -*- coding: utf-8 -*-
import logging
# Define your item pipelines here
from scrapy.exceptions import DropItem
from twisted.enterprise import adbapi

from MovieComments.items import MoviecommentsItem


class MoviecommentPipeline(object):


    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        '''init connection string'''
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8mb4',
            use_unicode=True,
            cp_reconnect=True)
        dbpool = adbapi.ConnectionPool('pymysql', **dbargs)
        return cls(dbpool)

    def process_item(self, item, spider):
        if isinstance(item, MoviecommentsItem):
            d = self.dbpool.runInteraction(self._conditional_insert, item, spider)
            d.addErrback(self._handle_error, item, spider)
            # at the end return the item in case of success or failure
            d.addBoth(lambda _: item)
            # return the deferred instead the item. This makes the engine to
            # process next item (according to CONCURRENT_ITEMS setting) after this
            # operation (deferred) has finished.
            return d
        else:
            return item



    def _conditional_insert(self,conn,item,spider):

        #print('Pipeline is starting...')
        conn.execute("""insert ignore into movie_comment 
               (title,author,comment_time,episode,
               albumurl,videourl,commentId,site,comment,ctime)
               values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""",
                     (
                     item['title'], item['author'], item['comment_time'], item['episode'], item['albumurl'], item['videourl'],
                     item['commentId'],item['site'], item['comment'],item['ctime']))
        #logging.info("Item updated in db: %s %r" % (item['title'], item))

    def close_spider(self, spider):
        """
        该方法用于数据插入完成后关闭数据库
        """
        self.dbpool.close()

    def _handle_error(self, failure, item, spider):
        """Handle occurred on db interaction."""
        # do nothing, just log
        logging.error(failure)


class DuplicatesPipeline(object):


     def __init__(self):
        self.book_set = set()


     def process_item(self, item, spider):
        name = item['commentId']
        if name in self.book_set:
            raise DropItem("Duplicate book found: %s" % item)


        self.book_set.add(name)
        return item