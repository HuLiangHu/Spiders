# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from datetime import datetime
from hashlib import md5
import logging
from scrapy.exceptions import DropItem
from twisted.enterprise import adbapi
from news.items import *
        
class MSSqlPipeline(object):
    """A pipeline to store the item in a MySQL database.
    This implementation uses Twisted's asynchronous database API.
    """
    def __init__(self, dbpool):
        self.dbpool = dbpool
    
    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MSSQL_HOST'],
            database=settings['MSSQL_DBNAME'],
            user=settings['MSSQL_USER'],
            password=settings['MSSQL_PASSWD']
        )
        dbpool = adbapi.ConnectionPool('pymssql', **dbargs)
        return cls(dbpool)
        
    def process_item(self,item,spider):
        # run db query in the thread pool
        if isinstance(item, News):
            d = self.dbpool.runInteraction(self._do_news_insert, item, spider)
        d.addErrback(self._handle_error, item, spider)
        # at the end return the item in case of success or failure
        d.addBoth(lambda _: item)
        # return the deferred instead the item. This makes the engine to
        # process next item (according to CONCURRENT_ITEMS setting) after this
        # operation (deferred) has finished.
        return d

    def _do_news_insert(self, conn, item, spider): 
        """Perform an insert or update.""" 
        conn.execute("""insert into xz_export_news_t1 
        (oid,personid,title,website,publish_at,url)
        values(%s,%s,%s,%s,%s,%s);""", 
        (item['oid'],item['personid'],item['title'],
        item['website'],item['publish_at'],item['url']))
        logging.info("Item updated in db: %s %r" % (item['url'], item))

    def _handle_error(self, failure, item, spider):
        """Handle occurred on db interaction."""
        # do nothing, just log
        logging.error(failure)


