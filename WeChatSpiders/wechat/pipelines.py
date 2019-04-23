# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from datetime import datetime
from hashlib import md5
from scrapy.exceptions import DropItem
from twisted.enterprise import adbapi
from wechat.items import *
import logging
import sys
import ujson
        
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
            cp_reconnect = True,
        )
        dbpool = adbapi.ConnectionPool('pymysql', **dbargs)
        return cls(dbpool)
        
    def process_item(self,item,spider):
        # run db query in the thread pool
        if isinstance(item, WeChatIndex):
            d = self.dbpool.runInteraction(self._do_WeChatIndex_upsert, item, spider) 
            
        
        d.addErrback(self._handle_error, item, spider)
        # at the end return the item in case of success or failure
        d.addBoth(lambda _: item)
        # return the deferred instead the item. This makes the engine to
        # process next item (according to CONCURRENT_ITEMS setting) after this
        # operation (deferred) has finished.
        return d
    
    
    
    def _do_WeChatIndex_upsert(self, conn, item, spider): 
        """Perform an insert or update.""" 
        conn.execute("""replace into `tbl_WeChatIndex` 
        (`keyword`,`total`,`day`)
        values(%s,%s,%s);""", 
        (item['keyword'],item['total'],item['day']))
        logging.info("Item updated in db: %s %r" % (item['keyword'], item))
    
   
    def _handle_error(self, failure, item, spider):
        """Handle occurred on db interaction."""
        # do nothing, just log
        logging.error(failure)


