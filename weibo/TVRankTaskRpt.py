#!/usr/bin/env python
# -*- coding: utf8 -*-

import pymongo
import logging
import datetime
import re
import pymysql
from  redis import Redis
import time
import datetime
import pytz
from elasticsearch import Elasticsearch


MONGOD_HOST = '10.10.121.66'
MONGOD_PORT = 27017
USEDB = 'weibo'

MYSQL_SERVER = 'mysql.crotondata.cn'
MYSQL_USER = ''
MYSQL_PASSWORD = ''
MYSQL_DB = 'newmedia_db'
MYSQL_PORT = 3306


tz = pytz.FixedOffset(480)

def _default_mongo(host=MONGOD_HOST, port=MONGOD_PORT, usedb=USEDB):
    connection = pymongo.MongoClient(host=host, port=port, j=True, w=1)
    db = connection.admin
    #db.authenticate('root', 'root')
    db = getattr(connection, usedb)
    return db

from elasticsearch import RequestsHttpConnection

class MyConnection(RequestsHttpConnection):
    def __init__(self, *args, **kwargs):
        proxies = kwargs.pop('proxies', {})
        super(MyConnection, self).__init__(*args, **kwargs)
        self.session.proxies = proxies

#es = Elasticsearch([{'host':'121.196.215.94'}],timeout=5000)
es = Elasticsearch([{'host':'10.10.121.66'}],timeout=5000)

logging.info(es.info())

class TVRank(object):
    def __init__(self, host=MONGOD_HOST, port=MONGOD_PORT):
        self.db = _default_mongo(host, port, usedb=USEDB)
        #self.redis = Redis(host = REDIS_HOST,port=REDIS_PORT)
        logging.info('Mongod connect to {host}:{port}'.format(host=host, port=port))

    def generateRpt(self,cudate=datetime.date.today()):
        date = cudate - datetime.timedelta(days=1)
        todayDate = datetime.datetime(date.year, date.month, date.day,tzinfo=tz)
        albums = self.get_albums()
        for album in albums:
            regx = album
            today = date + datetime.timedelta(days=1)
            yesterday = date - datetime.timedelta(days=1)
            mustQuery = [{ 'range': { 'created_at': { 'gte': yesterday,
                                                      'lt': today } } }
                         ,{ 'term': { 'is_ad': False } }
                         ]
            boolQuery = { 
                            'must': mustQuery, 
                            "must_not": {
                                "exists": {
                                    "field": "retweeted_status"
                                }
                            }
                        }
            filterquery = { 
                'filtered':{
                    'query':{
                        'match': { 'text': {'query':regx,'type':'phrase'} }
                    },
                    'filter':{
                        'bool':  boolQuery
                    }
                } 
                
            }
            request = []
            req_head = {'index':'weibo','search_type':'dfs_query_then_fetch','type':'status','timeout':'5m'}
            req_ushead = {'index':'weibo','search_type':'dfs_query_then_fetch','type':'user','timeout':'5m'}
            #{ type: "user", query: { query: { has_child: { type: "status",
            #query: filterquery } }, aggs: { gender : { terms : { field :
            #"gender" } } } } },

            request.extend([req_ushead, {  'query':  { 'has_child': { 'type': "status", 'query': filterquery } }, 'aggs': { 'gender' : { 'terms' : { 'field' : "gender" } } } }])
            request.extend([req_head, {  'query': filterquery, 'aggs': { 'sentiments' : { 'terms' : { 'field' : "sentiments_text" } } } }])
            request.extend([req_head,{  'query': filterquery,"aggs" : { "totalCount" : { "sum" : {"field" : "reposts_count","script" : "_value + 1" }}}}])

            result = es.msearch(body = request)
            genderresult = result['responses'][0]['aggregations']['gender']['buckets']
            
            sentimentresult = result['responses'][1]['aggregations']['sentiments']['buckets']
            mysentiment = []
            mygender = []
            if(len(genderresult) > 0):
                for item in genderresult:
                    if item['key'] == "m":
                        mygender.append({'gender':'男','count':item['doc_count'],'color':'#49aef0'})
                    if item['key'] == "f":
                        mygender.append({'gender':'女','count':item['doc_count'],'color':'#ff9cb1'})
                
            
            if(len(sentimentresult) > 0):
                for item in sentimentresult:
                    if item['key'] == -1 or item['key'] == '-1':
                        mysentiment.append({'sen':'负面','count':item['doc_count'],'color':'#4f7f3f'})
                    if item['key'] == 1 or item['key'] == '1':
                        mysentiment.append({'sen':'正面','count':item['doc_count'],'color':'#ff443f'})
                    if item['key'] == 0 or item['key'] == '0':
                        mysentiment.append({'sen':'中性','count':item['doc_count'],'color':'#b0b0b0'})
           
            #totalcount = result['responses'][2]['aggregations']['totalCount']['value']
            totalcount = result['responses'][1]['hits']['total'] 
            self.db.albumranks.insert({'date':todayDate,'name':album,'gender':mygender,'sentiment':mysentiment,'comments':totalcount,'totalcomments':totalcount})

            #self.db.albumranks.update({'date':todayDate,'name':album},{'gender':mygender,'sentiment':mysentiment,'comments':totalcount,'totalcomments':totalcount},True)
            print(regx+str(totalcount))
            logging.debug(regx+str(totalcount))
    def get_albums(self):
        albums = []
        try:
            conn = pymysql.connect(
                user = MYSQL_USER,
                passwd = MYSQL_PASSWORD,
                db = MYSQL_DB,
                host = MYSQL_SERVER,
                charset = "utf8",
                use_unicode = True
                )
            cursor = conn.cursor()
            cursor.execute(
                'call sp_getDailyKeyWord();'
                )
            rows = cursor.fetchall()
            for row in rows:
                keyword = re.sub('[ \d]+$','',row[0])
                keyword = re.sub('\(.*\)','',keyword)
                keyword = re.sub('（.*）','',keyword)
                keyword = re.sub(u'第.*季','',keyword)
                albums.append(keyword) 
            return albums 
        except Exception as e:
            print(e)
        finally:
            conn.close()
            return albums
if __name__ == "__main__":
    tvrank = TVRank()
   
    for i in range(0,1):
        date = datetime.date.today() - datetime.timedelta(days=i)
        tvrank.generateRpt(date)  
