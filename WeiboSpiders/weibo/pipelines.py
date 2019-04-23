# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from datetime import datetime
from hashlib import md5
from scrapy.exceptions import DropItem
from twisted.enterprise import adbapi
from weibo.items import *
import logging
import sys
import ujson
# from kafka import KafkaProducer
        
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
        if isinstance(item, WeiboIndex):
            d = self.dbpool.runInteraction(self._do_weiboindex_upsert, item, spider)
        if isinstance(item, WeiboStats):
            d = self.dbpool.runInteraction(self._do_weibostats_upsert, item, spider)
        if isinstance(item, WeiboIndexId):
            d = self.dbpool.runInteraction(self._do_weiboindexid_upsert, item, spider)
            
        
        d.addErrback(self._handle_error, item, spider)
        # at the end return the item in case of success or failure
        d.addBoth(lambda _: item)
        # return the deferred instead the item. This makes the engine to
        # process next item (according to CONCURRENT_ITEMS setting) after this
        # operation (deferred) has finished.
        return d
    
    def _do_weiboindexid_upsert(self,conn,item,spider):
        """Perform an insert or update.""" 
        conn.execute("""call sp_update_weiboindex_keyword (%s,%s)""",
        (item['word'],item['wid']))
        logging.info("Item updated in db: %s %r" % (item['word'], item))
    
    def _do_weiboindex_upsert(self, conn, item, spider): 
        """Perform an insert or update.""" 
        conn.execute("""replace into `tbl_weiboindex` 
        (`wid`,`pc`,`mobile`,`total`,`day`,`keyword`)
        values(%s,%s,%s,%s,%s,%s);""",
        (item['wid'],item['pc'],item['mobile'],
        item['total'],item['day'],item['keyword']))
        logging.info("Item updated in db: %s %r" % (item['wid'], item))
    
    def _do_weibostats_upsert(self, conn, item, spider): 
        """Perform an insert or update."""
        conn.execute("""replace into `tbl_weibostats` 
        (`weiboid`,`followers_count`,`friends_count`,`statuses_count`,`day`)
        values(%s,%s,%s,%s,%s);""",
        (item['weiboid'],item['followers_count'],item['friends_count'],
        item['statuses_count'],item['day']))
        logging.info("Item updated in db: %s %r" % (item['weiboid'], item))

    def _handle_error(self, failure, item, spider):
        """Handle occurred on db interaction."""
        # do nothing, just log
        logging.error(failure)


#
#
# class KafkaPipeline(object):
#     '''
#     Pushes a serialized item to appropriate Kafka topics.
#     '''
#
#     def __init__(self, producer, topic):
#         self.producer = producer
#         self.topic = topic
#         #self.appid_topics = appids
#         logging.debug("Setup kafka pipeline")
#         #self.use_base64 = use_base64
#
#     @classmethod
#     def from_settings(cls, settings):
#         try:
#             producer = KafkaProducer(bootstrap_servers=settings['KAFKA_HOSTS'],
#                                      retries=3,
#                                      linger_ms=settings['KAFKA_PRODUCER_BATCH_LINGER_MS'],
#                                      buffer_memory=settings['KAFKA_PRODUCER_BUFFER_BYTES'])
#         except Exception as e:
#             logging.error("Unable to connect to Kafka in Pipeline"\
#                 ", raising exit flag.")
#             # this is critical so we choose to exit.
#             # exiting because this is a different thread from the crawlers
#             # and we want to ensure we can connect to Kafka when we boot
#             sys.exit(1)
#         topic = settings['KAFKA_TOPIC']
#         #use_base64 = settings['KAFKA_BASE_64_ENCODE']
#
#         return cls(producer, topic)
#
#     @classmethod
#     def from_crawler(cls, crawler):
#         return cls.from_settings(crawler.settings)
#
#     def _get_time(self):
#         '''
#         Returns an ISO formatted string of the current time
#         '''
#         return datetime.utcnow().isoformat()
#
#     def process_item(self, item, spider):
#         try:
#             logging.debug("Processing item in KafkaPipeline")
#             datum = dict(item)
#             datum["timestamp"] = self._get_time()
#
#             try:
#                 #if self.use_base64:
#                     #datum['body'] = base64.b64encode(bytes(datum['body'], 'utf-8'))
#                 message = ujson.dumps(datum, sort_keys=True)
#             except Exception as e:
#                 logging.error(e.message)
#                 message = 'json failed to parse'
#             self.producer.send(self.topic, message, key=str(datum['id']))
#
#
#
#         except Exception as e:
#             logging.error(e.message)
#         return item
#
#     def close_spider(self, spider):
#         logging.info("Closing Kafka Pipeline")
#         self.producer.flush()
#         self.producer.close(timeout=10)