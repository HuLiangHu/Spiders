# -*- coding: utf-8 -*-
import csv
import time
# from twisted.internet.threads import deferToThread
# import logging
# from items import WeiboItem, UserItem, Relation,TopicItem,CommentItem,HotTopicItem,Retweetmap
# import pymongo
# from  redis import Redis
# from datetime import datetime


# MONGOD_HOST = '127.0.0.1'
# MONGOD_PORT = 27017
# USEDB = 'weibo'
#
# REDIS_HOST = '127.0.0.1'
# REDIS_PORT = 6379
# UNPROCESSEDWEIBO_KEY = 'social:weibo:unprocessed'
# UNPROCESSEDWEIBOCOMMENT_KEY = 'social:weibocomment:unprocessed'
#
# def _default_mongo(host=MONGOD_HOST, port=MONGOD_PORT, usedb=USEDB):
#     connection = pymongo.MongoClient(host=host, port=port, j=True, w=1)
#     db = connection.admin
#     #db.authenticate('root', 'root')
#     db = getattr(connection, usedb)
#     return db
#
#
# class FilePipeline(object):
#     def process_item(self, item, spider):
#          with open('userids.txt', 'a') as f:
#              f.write('%s,%s\n'%(item['url'],item['uid']))
#          return item
#
# class MongodbPipeline(object):
#     """
#     insert and update items to mongod
#     > use test
#     switched to db test
#     > db.simple.insert({a: 1})
#     > db.simple.find()
#     { "_id" : ObjectId("50af9034d086dd9cd0ba3275"), "a" : 1 }
#     > db.simple.update({"a": 1}, {$addToSet: {"b": 2}})
#     > db.simple.find()
#     { "_id" : ObjectId("50af9034d086dd9cd0ba3275"), "a" : 1, "b" : [ 2 ] }
#     > db.simple.update({"a": 1}, { $addToSet : { a : { $each : [ 3 , 5 , 6 ] }
#     > } })
#     Cannot apply $addToSet modifier to non-array
#     > db.simple.update({"a": 1}, { $addToSet : { b : { $each : [ 3 , 5 , 6 ] }
#     > } })
#     > db.simple.find()
#     { "_id" : ObjectId("50af9034d086dd9cd0ba3275"), "a" : 1, "b" : [ 2, 3, 5, 6 ] }
#     > db.simple.update({"a": 1}, { $addToSet : { b : { $each : [ 3 , 5 , 6 ] }
#     > } })
#     > db.simple.find()
#     { "_id" : ObjectId("50af9034d086dd9cd0ba3275"), "a" : 1, "b" : [ 2, 3, 5, 6 ] }
#     > db.simple.update({"a": 1}, { $addToSet : { a : { $each : [ 3 , 5 , 6 ] }
#     > } })
#     Cannot apply $addToSet modifier to non-array
#     > db.simple.update({"a": 1}, {$addToSet: {"b": [2,7]}})
#     > db.simple.find()
#     { "_id" : ObjectId("50af9034d086dd9cd0ba3275"), "a" : 1, "b" : [ 2, 3, 5, 6, [ 2, 7 ] ] }
#     > db.simple.update({"a": 1}, {$set: {"c": []}})
#     > db.simple.find()
#     { "_id" : ObjectId("50af9034d086dd9cd0ba3275"), "a" : 1, "b" : [ 2, 3, 5, 6, [ 2, 7 ] ], "c" : [ ] }
#     > db.simple.update({"a": 1}, { $addToSet : { c : { $each : [ 3 , 5 , 6 ] }
#     > } })
#     > db.simple.find()
#     { "_id" : ObjectId("50af9034d086dd9cd0ba3275"), "a" : 1, "b" : [ 2, 3, 5, 6, [ 2, 7 ] ], "c" : [ 3, 5, 6 ] }
#     """
#
#     def __init__(self, host=MONGOD_HOST, port=MONGOD_PORT,redis_host = REDIS_HOST,redis_port = REDIS_PORT):
#         self.db = _default_mongo(host, port, usedb=USEDB)
#         self.redis = Redis(host = redis_host,port=redis_port)
#         logging.log(logging.INFO, 'Mongod connect to {host}:{port}'.format(host=host, port=port))
#
#     @classmethod
#     def from_settings(cls, settings):
#         host = settings.get('MONGOD_HOST', MONGOD_HOST)
#         port = settings.get('MONGOD_PORT', MONGOD_PORT)
#         redis_host = settings.get('REDIS_HOST', REDIS_HOST)
#         redis_port = settings.get('REDIS_PORT', REDIS_PORT)
#         return cls(host, port,redis_host,redis_port)
#
#     @classmethod
#     def from_crawler(cls, crawler):
#         return cls.from_settings(crawler.settings)
#
#     def process_item(self, item, spider):
#         if isinstance(item, Retweetmap):
#             return deferToThread(self.process_retweetmap, item, spider)
#         if isinstance(item, HotTopicItem):
#             return deferToThread(self.process_hottopic, item, spider)
#         if isinstance(item, CommentItem):
#             return deferToThread(self.process_comment, item, spider)
#         if isinstance(item, WeiboItem):
#             return deferToThread(self.process_weibo, item, spider)
#         elif isinstance(item, UserItem):
#             return deferToThread(self.process_user, item, spider)
#         elif isinstance(item, Relation):
#             return deferToThread(self.process_relation, item, spider)
#         elif isinstance(item, TopicItem):
#             return deferToThread(self.process_topic, item, spider)
#
#     def process_item_sync(self, item, spider):
#         if isinstance(item, Retweetmap):
#             return self.process_retweetmap(item, spider)
#         if isinstance(item, HotTopicItem):
#             return self.process_hottopic(item, spider)
#         if isinstance(item, CommentItem):
#             return self.process_comment(item, spider)
#         if isinstance(item, WeiboItem):
#             return self.process_weibo(item, spider)
#         elif isinstance(item, UserItem):
#             return self.process_user(item, spider)
#         elif isinstance(item, Relation):
#             return self.process_relation(item, spider)
#
#     def process_retweetmap(self,item,spider):
#         retweetmap = item.to_dict()
#         if not self.db.retweetmaps.find({'statusid': retweetmap['statusid']}).count():
#             self.db.retweetmaps.insert(retweetmap)
#         return item
#
#     def process_weibo(self, item, spider):
#         weibo = item.to_dict()
#         weibo['_id'] = weibo['id']
#         if self.db.status.find({'_id': weibo['_id']}).count()>0:
#             logging.debug('Found status %s .' %weibo['_id'])
#             updates = {}
#             updates['last_modify'] = time.time()
#             for key in WeiboItem.PIPED_UPDATE_KEYS:
#
#                 if weibo.get(key) is not None:
#                     updates[key] = weibo[key]
#
#             # reposts
#             if 'task_keys' in weibo:
#                 updates_modifier = {'$set': updates, '$addToSet': {'task_keys': {'$each': weibo['task_keys']},'reposts': {'$each': weibo['reposts']}}}
#             else:
#                 updates_modifier = {'$set': updates, '$addToSet': {'reposts': {'$each': weibo['reposts']}}}
#             self.redis.rpush(UNPROCESSEDWEIBO_KEY,weibo['_id'])
#             self.db.status.update({'_id': weibo['_id']}, updates_modifier)
#         else:
#
#             weibo['first_in'] = time.time()
#             weibo['last_modify'] = weibo['first_in']
#             self.redis.rpush(UNPROCESSEDWEIBO_KEY,weibo['_id'])
#             self.db.status.insert(weibo)
#
#         return item
#
#     def process_hottopic(self, item, spider):
#         topic = item.to_dict()
#         topic['created_at'] = time.time()
#         self.db.hottopics.insert(topic)
#         self.db.hottopicsrank.update({'title':topic['title']},{'date':topic['rankdate'] ,'title':topic['title'],'host':topic['host'],'desc':topic['desc'],'readcount':topic['readcount'],'readcount_fixed':topic['readcount_fixed']},upsert = True)
#         return item
#
#     def process_comment(self, item, spider):
#         comment = item.to_dict()
#         comment['_id'] = comment['id']
#
#         if not self.db.comments.find({'_id': comment['_id']}).count():
#             comment['first_in'] = time.time()
#             comment['last_modify'] = comment['first_in']
#             self.redis.rpush(UNPROCESSEDWEIBOCOMMENT_KEY,comment['_id'])
#             self.db.comments.insert(comment)
#
#         return item
#
#     def process_user(self, item, spider):
#         if 'tags' in item and len(item['tags'])>0 and 'flag' in item['tags'][0]:
#             item['tags'] = []
#         user = item.to_dict()
#         user['_id'] = user['id']
#         if self.db.users.find({'_id': user['_id']}).count():
#             updates = {}
#             updates['last_modify'] = time.time()
#             for key in UserItem.PIPED_UPDATE_KEYS:
#                 if user.get(key) is not None:
#                     updates[key] = user[key]
#
#             updates_modifier = {'$set': updates,
#                                 '$addToSet': {
#                                     'followers': {'$each': user['followers']},
#                                     'friends': {'$each': user['friends']}
#                                 }}
#             self.db.users.update({'_id': user['_id']}, updates_modifier)
#         else:
#             user['first_in'] = time.time()
#             user['last_modify'] = user['first_in']
#             self.db.users.insert(user)
#
#         return item
#
#     def process_relation(self,item,spider):
#         relation = item.to_dict()
#         if not self.db.relation.find({'uid':relation['uid'],'friend_uid':relation['friend_uid']}).count():
#             relation['first_in'] = time.time()
#             relation['last_modify'] = relation['first_in']
#             self.db.relation.insert(relation)
#         return item
#
#     def process_topic(self,item,spider):
#         topic = item.to_dict()
#         if not self.db.topicstats.find({'topic':topic['topic'],'date':topic['date']}).count():
#             topic['created_at'] = time.time()
#             self.db.topicstats.insert(topic)
#         return item

class MyCSVPipeline(object):
    def process_item(self, item, spider):
        f = open('../weibo/%s.csv'%item['task_keys'][0], 'a', encoding='ANSI', errors='ignore',newline='')
        writer = csv.writer(f)
        writer.writerow((
            item['attitudes_count'], str(item['clear_text']).strip(), item['comments'], item['comments_count'], item['created_at'],item['followers_count'],
            item['id'],item['idstr'], item['mid'], item['reposts'], item['reposts_count'], item['source'],
            item['task_keys'][0], str(item['text']).strip(), item['user_id'], item['user_name']))
        return item