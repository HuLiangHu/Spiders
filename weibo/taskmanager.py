#!/usr/bin/env python
# -*- coding: utf8 -*-

import pymongo
import datetime
import re
from  redis import Redis
import time
import pytz
import logging

MONGOD_HOST = '10.10.121.66'
MONGOD_PORT = 27017
USEDB = 'weibo'

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
START_URLS = 'search:start_urls'

SEARCH_URL = 'https://c.api.weibo.com/2/search/statuses/limited.json?antispam=0&dup=1&q=%s&access_token=2.00ZLWYdC0KWpTW73ca4f3acb4k45rD&starttime=%d&endtime=%d&onlynum=1'
TIMELIME_URL = 'https://c.api.weibo.com/2/search/statuses/limited.json?ids=%s&count=50&page=1&access_token=2.00ZLWYdC0KWpTW73ca4f3acb4k45rD&t=%s'

tz = pytz.FixedOffset(480)
utc = pytz.timezone('utc')

def _default_mongo(host=MONGOD_HOST, port=MONGOD_PORT, usedb=USEDB):
    connection = pymongo.MongoClient(host=host, port=port, j=True, w=1)
    db = connection.admin
    db = getattr(connection, usedb)
    return db

class TaskManager(object):
    def __init__(self, host=MONGOD_HOST, port=MONGOD_PORT):
        self.db = _default_mongo(host, port, usedb=USEDB)
        self.redis = Redis(host = REDIS_HOST,port=REDIS_PORT)

    def loadtasks(self):
        self._loadtask_yuqin()
        self._loadtask_chuanbo()
        if datetime.datetime.now().hour>20:
            self._loadtask_weibo()

    
    ############################################### 传播分析 ################################################
    def _loadtask_chuanbo(self):
        tasks = self.db.weibolinkstasks.find({'status':{'$in':[0,1]}}) 
        for task in tasks:
            self.redis.rpush('comments:start_urls',task['weibo']['idstr'])
            self.redis.rpush('reposts:start_urls',task['weibo']['idstr'])
            now = datetime.datetime.now(tz)
            self.db.weibolinkstasks.update({'_id':task['_id']},{'$set':{'status':2,'analysis_at':now}})

    ############################################### 微博分析 ################################################
    def _loadtask_weibo(self):
        tasks = self.db.weibomonitors.find().distinct('weiboid')
        for task in tasks:
            
            self.redis.rpush('timeline:start_urls',TIMELIME_URL % (str(task),str(time.time())))
    ############################################### 舆情任务 ################################################
    def _loadtask_yuqin(self):
        '''
        状态 ：0 新建，1 执行中 2 已完成 -1,删除
        '''
        tasks = self.db.tasks.find({'status':{"$in":[0,1]}})
        for task in tasks:
            self._inittask_yuqin(task) 

    '''
    舆情任务
    '''
    def _inittask_yuqin(self,task):
        try:
            now = datetime.datetime.now(tz)
            if 'dayago' in task and task['dayago']:
                if task['startDate'].replace(tzinfo=utc).astimezone(tz) > now - datetime.timedelta(days=1):
                    logging.debug('等待运行')
                elif task['endDate'].replace(tzinfo=utc).astimezone(tz)  > now - datetime.timedelta(days=1): 
                    
                    if task['status'] == 1:
                        
                        fromTime = int(time.mktime(task['updatedDate'].replace(tzinfo=utc).astimezone(tz).timetuple()) )
                        toTime = int(time.mktime((now - datetime.timedelta(days=1)).timetuple()) )
                        self.redis.rpush(START_URLS,SEARCH_URL%(task['keyword'],fromTime,toTime))
                        self.db.tasks.update({'_id':task['_id']},{'$set':{'updatedDate':now - datetime.timedelta(days=1)}})
                    else:
                        fromTime = int(time.mktime(task['startDate'].replace(tzinfo=utc).astimezone(tz).timetuple()) )
                        
                        toTime = int(time.mktime((now - datetime.timedelta(days=1)).timetuple()) )
                        self.redis.rpush(START_URLS,SEARCH_URL%(task['keyword'],fromTime,toTime))
                        self.db.tasks.update({'_id':task['_id']},{'$set':{'status':1,'updatedDate':now - datetime.timedelta(days=1)}})
                elif task['endDate'].replace(tzinfo=tz).astimezone(tz)  <= now -datetime.timedelta(days=1): 
                    fromTime = int(time.mktime(task['startDate'].replace(tzinfo=utc).astimezone(tz).timetuple()) )
                    toTime = int(time.mktime(task['endDate'].replace(tzinfo=utc).astimezone(tz).timetuple()) )
                    self.redis.rpush(START_URLS,SEARCH_URL%(task['keyword'],fromTime,toTime))
                    self.db.tasks.update({'_id':task['_id']},{'$set':{'status':2,'updatedDate':now}})  
            else:                    
                if task['startDate'].replace(tzinfo=utc).astimezone(tz) > now :
                    logging.debug('等待运行')
                elif task['endDate'].replace(tzinfo=utc).astimezone(tz)  > now:
                    if task['status'] == 1:
                        fromTime = int(time.mktime(task['updatedDate'].replace(tzinfo=utc).astimezone(tz).timetuple()) )
                        toTime = int(time.mktime(now.timetuple()) )
                        self.redis.rpush(START_URLS,SEARCH_URL%(task['keyword'],fromTime,toTime))
                        self.db.tasks.update({'_id':task['_id']},{'$set':{'updatedDate':now}})
                        
                    else:
                        
                        fromTime = int(time.mktime(task['startDate'].replace(tzinfo=utc).astimezone(tz).timetuple()) )
                        toTime = int(time.mktime(now.timetuple()) )
                        self.redis.rpush(START_URLS,SEARCH_URL%(task['keyword'],fromTime,toTime))
                        self.db.tasks.update({'_id':task['_id']},{'$set':{'status':1,'updatedDate':now}})
                elif task['endDate'].replace(tzinfo=tz).astimezone(tz)  <= now: 
                    
                    fromTime = int(time.mktime(task['startDate'].replace(tzinfo=utc).astimezone(tz).timetuple()) ) 
                    toTime = int(time.mktime(task['endDate'].replace(tzinfo=utc).astimezone(tz).timetuple()) )
                    
                    self.redis.rpush(START_URLS,SEARCH_URL%(task['keyword'],fromTime,toTime))
                    self.db.tasks.update({'_id':task['_id']},{'$set':{'status':2,'updatedDate':now}})  
        except Exception as e:
            logging.error(e)


if __name__ == "__main__":
    tm = TaskManager()
    tm.loadtasks()
    
