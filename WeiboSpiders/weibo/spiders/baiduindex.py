# # -*- coding: utf-8 -*-
# import time
#
# import scrapy
# from urllib.parse import urlencode
# import datetime
# import execjs
# import requests
# import json
# import time
# import random
#
# from WeiboSpiders.weibo.settings import COOKIES
#
#
# class BaiduindexSpider(scrapy.Spider):
#     name = 'baiduindex'
#     # allowed_domains = ['baidu.com']
#     # start_urls = ['http://baidu.com/']
#     search_index_url = 'https://index.baidu.com/api/SearchApi/index?'  # 搜索指数
#     media_index_url = 'https://index.baidu.com/api/NewsApi/getNewsIndex?'  # 媒体指数
#     resource_url = 'https://index.baidu.com/api/FeedSearchApi/getFeedIndex?'  # 资讯指数
#
#     day = 30  # 查询时间
#     startDate = datetime.datetime(2019, 1, 26)
#     endDate = datetime.datetime(2019, 2, 25)
#
#     now = int(time.time()) * 1000
#     item_list = []
#     with open(r'D:\Projects\myspiders\spider-BaiduIndex\new_spider_without_selenium\keyword.txt', 'r',
#               encoding='utf-8') as f:
#         keywords = f.readlines()
#
#     def start_requests(self):
#         for i,keyword in enumerate(self.keywords):
#             parmas = {
#                 'area': '0',
#                 'word': keyword,
#                 # 'days': self.day
#                 'startDate': str(self.startDate).split(' ')[0],
#                 'endDate': str(self.endDate).split(' ')[0]
#             }
#             headers = {
#                 'Host': 'index.baidu.com',
#                 #'Connection': 'keep-alive',
#                 'X-Requested-With': 'XMLHttpRequest',
#                 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
#                 'Cookie': COOKIES[i%len(COOKIES)]
#             }
#             url = self.media_index_url + urlencode(parmas)
#             yield scrapy.Request(url,headers=headers,cookies=self.stringToDict(headers['Cookie']),callback=self.parse_uniqid,meta={'parmas':parmas,'headers':headers,'keyword':keyword})
#
#
#     def parse_uniqid(self, response):
#         #print(json.loads(response.text)['message'])
#         if json.loads(response.text)['message'] =='success':
#             uniqid = json.loads(response.text)['data']['uniqid']
#             url = 'https://index.baidu.com/Interface/ptbk?uniqid={}'.format(uniqid)
#
#             yield scrapy.Request(url,callback=self.parse_sign_parmas_data,cookies=self.stringToDict(response.meta['headers']['Cookie']),
#                                  headers=response.meta['headers'],
#                                  meta={'headers':response.meta['headers'],
#                                        'parmas':response.meta['parmas'],
#                                        'keyword': response.meta['keyword']})
#
#     def parse_sign_parmas_data(self, response):
#
#         sign_parmas_data = json.loads(response.text)['data']
#         url = self.media_index_url + urlencode(response.meta['parmas'])
#         yield scrapy.Request(url, callback=self.parse_media_index, cookies=self.stringToDict(response.meta['headers']['Cookie']),
#                              headers=response.meta['headers'],
#                              meta={'headers': response.meta['headers'],
#                                    'parmas': response.meta['parmas'],
#                                    'sign_parmas_data':sign_parmas_data,
#                                    'keyword':response.meta['keyword']},
#                              dont_filter=True)
#
#     def parse_media_index(self, response):
#         #print(json.loads(response.text))
#         message = json.loads(response.text)['message']
#
#         if message == 'success':
#             for i in json.loads(response.text)['data']['index']:
#                 newsindex = i['data']
#             media_datas = self.getSign(response.meta['sign_parmas_data'], newsindex).split(',')
#             if media_datas == ['']:
#                 media_datas = [0] * self.day
#             else:
#                 media_datas = media_datas
#             url = self.search_index_url + urlencode(response.meta['parmas'])
#             yield scrapy.Request(url,callback=self.parse_search_index,meta={'headers': response.meta['headers'],
#                                                                             'parmas': response.meta['parmas'],
#                                                                             'sign_parmas_data':response.meta['sign_parmas_data'],
#                                                                             'media_datas':media_datas,
#                                                                             'keyword': response.meta['keyword']})
#     def parse_search_index(self, response):
#         print('message:', json.loads(response.text)['message'])
#         if json.loads(response.text)['message'] == 0:
#             for info in json.loads(response.text)['data']['userIndexes']:
#                 # 获取get_sign()函数的参数key
#                 all = info['all']['data']
#                 pc = info['pc']['data']
#                 mobile = info['wise']['data']
#             total_data = self.getSign(response.meta['sign_parmas_data'], all).split(',')
#             pc_data = self.getSign(response.meta['sign_parmas_data'], pc).split(',')
#             mobile_data = self.getSign(response.meta['sign_parmas_data'], mobile).split(',')
#             for i, (total, pc, mobile, media_index) in enumerate(zip(total_data, pc_data, mobile_data, response.meta['media_datas'])):
#
#                 item = {}
#                 item['total'] = self.fillnull(total)
#                 item['pc'] = self.fillnull(pc)
#                 item['mobile'] = self.fillnull(mobile)
#                 item['mediaindex']=self.fillnull(media_index)
#                 #item['resourceindex'] = self.fillnull(resource_data)
#                 item['keyword'] =response.meta['keyword']
#                 time_differ = int(str(self.endDate-self.startDate).split(' ')[0])#开始结束时间差
#
#                 timeStamp = int(time.mktime(self.endDate.timetuple())) #将最后一天转成时间戳
#                 lastday = timeStamp - 60 * 60 * 24 * (time_differ - i) #反推前一天的日期
#                 last = time.strftime('%Y-%m-%d', time.localtime(lastday))
#
#     #########按时间间隔########
#                 # lastday = self.now - 60 * 60 * 24 * (self.day - i+1)*1000
#                 # last = time.strftime('%Y-%m-%d', time.localtime(lastday/1000))
#     #########################
#                 item['day'] = last
#                 yield item
#
#     def get_parmas(self,parmas,headers):
#         url = self.media_index_url + urlencode(parmas)
#         response = requests.get(url, headers=headers,verify=False)
#         uniqid = json.loads(response.text)['data']['uniqid']
#         url = 'https://index.baidu.com/Interface/ptbk?uniqid={}'.format(uniqid)
#         response = requests.get(url, headers=headers,verify=False)
#         # 获取get_sign()函数参数data
#         t_data = json.loads(response.text)['data']
#         return t_data
#
#     def stringToDict(self,cookie):
#         '''
#         将从浏览器上Copy来的cookie字符串转化为Scrapy能使用的Dict
#         :return:
#         '''
#         itemDict = {}
#         items = cookie.split(';')
#
#         for item in items:
#             key = item.split('=')[0].replace(' ', '')
#             value = item.split('=')[1]
#             itemDict[key] = value
#         return itemDict
#
#     def getSign(self,key, data):
#         with open("baiduindex.js") as f:
#             jsData = f.read()
#
#         js = execjs.compile(jsData)
#         sign = js.call('decrypt', key, data)
#         return sign
#
#     def fillnull(self,s):
#         if s:
#             data = s
#         else:
#             data = 0
#         return data