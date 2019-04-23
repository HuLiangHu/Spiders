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
from variety.items import *

class VarietyPipeline(object):
    def process_item(self, item, spider):
        return item
        
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
        #d = self.dbpool.runInteraction(self._do_variety_upsert, item, spider) 
        if isinstance(item, VarietyItem):
            d = self.dbpool.runInteraction(self._do_variety_upsert, item, spider)
        elif  isinstance(item, VarietyVideoItem):
            d = self.dbpool.runInteraction(self._do_varietyvideo_upsert, item, spider)
        d.addErrback(self._handle_error, item, spider)
        # at the end return the item in case of success or failure
        d.addBoth(lambda _: item)
        # return the deferred instead the item. This makes the engine to
        # process next item (according to CONCURRENT_ITEMS setting) after this
        # operation (deferred) has finished.
        return d
    
    
    def _do_variety_upsert(self, conn, item, spider):  
        """Perform an insert or update."""
        hashcode = self._get_hashcode(item)
        item.setdefault('additional_infos', {})
        item.setdefault('area', None)
        item.setdefault('desc', None) 
        item.setdefault('host', None)
        item.setdefault('player', None)
        item.setdefault('cover_img', None)
        item.setdefault('category', None)
        item.setdefault('playStatus', None)
        item.setdefault('lastseries', None)
        item.setdefault('tags', None)
        item.setdefault('tv', None)
        item.setdefault('releaseDate', None) 
        conn.execute("""INSERT IGNORE into `tbl_variety_rawdata` 
        (`url`,`aid`,`hashcode`,`name`,`area`,
        `desc`,`cover_img`,`playDate`,
        `playCount`,`playStatus`,`host`,`player`,`category`,`tags`,
        `additional_infos`,`website`,
        `releaseDate`,`lastseries`,`tv`)
        values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""", 
        (item['url'],item['aid'],hashcode,item['name'],
        item['area'],item['desc'],
        item['cover_img'],item['playdate'],item['playCount'],
        item['playStatus'],item['host'],item['player'],item['category'],item['tags'],
        str(item['additional_infos']),
        item['website'],item['releaseDate'],item['lastseries'],item['tv']))
        logging.info("Item updated in db: %s %r" % (hashcode, item))
    

    def _do_varietyvideo_upsert(self, conn, item, spider): 
        """Perform an insert or update."""
        hashcode = self._get_hashcode(item)
        albumnhashcode = self._get_albumnhashcode(item)
        item.setdefault('additional_infos', {}) 
        item.setdefault('desc', None) 
        item.setdefault('player', None) 
        item.setdefault('video_img', None)  
        item.setdefault('releaseDate', None)
        
        conn.execute("""INSERT IGNORE into `tbl_varietyvideo_rawdata` 
        (`url`,`aid`,`vid`,`albumurl`,`albumnhashcode`,`hashcode`,`name`,
        `desc`,`video_img`,`playDate`,
        `playCount`,`player`,`additional_infos`,`website`,
        `releaseDate`)
        values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""", 
        (item['url'],item['aid'],item['vid'],item['albumurl'],albumnhashcode,hashcode,
        item['name'],item['desc'],
        item['video_img'],item['playdate'],item['playCount'],
        item['player'],str(item['additional_infos']),
        item['website'],item['releaseDate']))
        logging.info("Item updated in db: %s %r" % (hashcode, item))

    def _handle_error(self, failure, item, spider):
        """Handle occurred on db interaction."""
        # do nothing, just log
        logging.error(failure)

    def _get_hashcode(self, item):
        """Generates an unique identifier for a given item."""
        # hash based solely in the url field
        return md5(item['url'].encode('utf8')).hexdigest()
    def _get_albumnhashcode(self, item):
        """Generates an unique identifier for a given item."""
        # hash based solely in the url field
        return md5(item['albumurl'].encode('utf8')).hexdigest()
