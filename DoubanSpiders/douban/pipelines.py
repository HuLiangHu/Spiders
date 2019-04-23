# -*- coding: utf-8 -*-
'''Pipelines'''
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import logging
#from scrapy.exceptions import DropItem
from twisted.enterprise import adbapi
from twisted.internet.threads import deferToThread
from douban.items import DoubanMovieInfo


class MySqlPipeline(object):
    """A pipeline to store the item in a MySQL database.
    This implementation uses Twisted's asynchronous database API.
    """

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
            charset='utf8',
            use_unicode=True,
            cp_reconnect=True)
        dbpool = adbapi.ConnectionPool('pymysql', **dbargs)
        return cls(dbpool)

    def process_item(self, item, spider):
        ''' run db query in the thread pool '''
        if isinstance(item, DoubanMovieInfo):
            d = self.dbpool.runInteraction(
                self._do_doubanstats_upsert, item, spider)

        d.addErrback(self._handle_error, item, spider)
        # at the end return the item in case of success or failure
        d.addBoth(lambda _: item)
        # return the deferred instead the item. This makes the engine to
        # process next item (according to CONCURRENT_ITEMS setting) after this
        # operation (deferred) has finished.
        return d

    def _do_doubanstats_upsert(self, conn, item, spider):
        """Perform an insert or update."""
        conn.execute("""replace into `tbl_doubantv` 
        (`id`,`rating`,`ratings_count`,`comments_count`,
        `reviews_count`,`wish_count`,`collect_count`,`year`,
        `image`,`genres`,`countries`,`casts`,`episodes_count`,
        `title`,`original_title`,`directors`,`aka`,`type`,`duration`)
        values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""",
                     (item['id'], item['rating'], item['ratings_count'], item['comments_count'], item['reviews_count'], item['wish_count'],
                      item['collect_count'], item['year'], item['image'], item[
                          'genres'], item['countries'], item['casts'],
                         item['episodes_count'], item['title'], item['original_title'], item['directors'], item['aka'], item['type'],item['duration']))
        logging.info("Item updated in db: %s %r" % (item['id'], item))

    def _handle_error(self, failure, item, spider):
        """Handle occurred on db interaction."""
        # do nothing, just log
        logging.error(failure)

'''
MONGOD_URL = 'mongodb://localhost:27017/media'


class MongodbPipeline(object):
    """MongoDB Pipeline"""
    
    @classmethod
    def from_settings(cls, settings):
        mongod_url = settings.get('MONGOD_URL', MONGOD_URL)
        upset_fields = settings.get('UPSET_FIELDS', [])
        mongo_default_connection = settings.get(
            'MONGOD_DEFAULT_COLLECTION', 'other')

        return cls(mongod_url, upset_fields, mongo_default_connection)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    def __init__(self, mongod_url, upset_fields, mongo_default_connection):
        client = pymongo.MongoClient(mongod_url)
        self.db = client.get_default_database()
        self.UPSET_FIELDS = upset_fields
        self.MONGOD_DEFAULT_COLLECTION = mongo_default_connection

    def _preitem(self, item):
        """Preper Items  """
        insertObj = {}
        updateObj = {}
        upset_fields = item['_sys_upset_fields'] or self.UPSET_FIELDS
        for field in item:
            if not field.startswith('_sys_'):
                if field in upset_fields:
                    updateObj[field] = item[field]
                else:
                    insertObj[field] = item[field]
        return insertObj, updateObj

    def process_item(self, item, spider):
        return deferToThread(self._process_item, item, spider)

    def _process_item(self, item, spider):
        insertObj, updateObj = self._preitem(item)
        if '_sys_collection' in item:
            if updateObj:
                self.db[item['_sys_collection']].update(
                    {'_id': item['id']}, {'$set': updateObj, '$setOnInsert': insertObj}, upsert=True)
            else:
                self.db[item['_sys_collection']].update(
                    {'_id': item['id']}, {'$set': insertObj}, upsert=True)
        else:
            if updateObj:
                self.db[self.MONGOD_DEFAULT_COLLECTION].update(
                    {'_id': item['id']}, {'$set': updateObj, '$setOnInsert': insertObj}, upsert=True)
            else:
                self.db[self.MONGOD_DEFAULT_COLLECTION].update(
                    {'_id': item['id']}, {'$set': insertObj}, upsert=True)
'''