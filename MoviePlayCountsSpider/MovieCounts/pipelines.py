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
from MovieCounts.items import MoviecountsItem



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
        if item['title']!=None:
            query = self.dbpool.runInteraction(self._conditional_insert, item,spider)  # 调用插入的方法
            query.addErrback(self._handle_error, item, spider)  # 调用异常处理方法
            return item
        else:
            print("------------------------------------------------------------")


    def _conditional_insert(self,conn,item,spider):
        conn.execute("""replace into tbl_moviescounts (title,viewcount,website,createdtime,url
                )  values(%s,%s,%s,%s,%s);""",
                     (item['title'], item['view_count'], item['comefrom'], item['datetime'],item["url"]
                      ))

    def _handle_error(self, failure, item, spider):
        """Handle occurred on db interaction."""
        # do nothing, just log
        logging.error(failure)

