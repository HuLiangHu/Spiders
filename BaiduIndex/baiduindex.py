import csv
import random
import time
from urllib.parse import urlencode
import execjs
import pymysql
import requests
import json
import re
import datetime
from Cookies import COOKIES

class BaiDuIndex(object):
    def __init__(self,keyword,cookie):
        self.search_index_url = 'https://index.baidu.com/api/SearchApi/index?'#搜索指数
        self.media_index_url = 'https://index.baidu.com/api/NewsApi/getNewsIndex?'#媒体指数
        self.resource_url ='https://index.baidu.com/api/FeedSearchApi/getFeedIndex?'#资讯指数
        self.keyword = keyword
        self.day = 169 #查询时间
        self.startDate= datetime.datetime(2019,3,24)
        self.endDate =datetime.datetime(2019,4,11)
        self.time_differ = int(str(self.endDate - self.startDate).split(' ')[0])  # 开始结束时间差
        self.parmas = {
            'area': '0',
            'word': keyword,
            #'days': self.day
            'startDate':str(self.startDate).split(' ')[0],
            'endDate':str(self.endDate).split(' ')[0]
        }
        self.now = int(time.time()) * 1000
        self.item_list =[]
        self.headers = {
            'Host': 'index.baidu.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
            'Cookie': cookie,
            'Proxy-Authorization': 'Basic ' + appKey
        }
        self.proxy = {"http": "http://" + ip_port, "https": "https://" + ip_port}

    def stringToDict(self,cookie):
        '''
        将从浏览器上Copy来的cookie字符串转化为Scrapy能使用的Dict
        :return:
        '''
        itemDict = {}
        items = cookie.split(';')

        for item in items:
            key = item.split('=')[0].replace(' ', '')
            value = item.split('=')[1]
            itemDict[key] = value
        return itemDict

    def getSign(self,key, data):
        with open("baiduindex.js") as f:
            jsData = f.read()

        js = execjs.compile(jsData)
        sign = js.call('decrypt', key, data)
        return sign

    def fillzero(self,data):
        if data == ['']:
            new_data = [0] * self.time_differ #按指定时间：time_differ，按日期间隔：day
        else:
            new_data = data
        return new_data

    def fillnull(self,s):
        if s:
            data = s
        else:
            data = 0
        return data

    def get_parmas(self):

        url = self.media_index_url + urlencode(self.parmas)
        response = requests.get(url, headers=self.headers,verify=False)
        uniqid = json.loads(response.text)['data']['uniqid']
        url = 'https://index.baidu.com/Interface/ptbk?uniqid={}'.format(uniqid)
        response = requests.get(url, headers=self.headers,verify=False)
        #获取get_sign()函数参数data
        t_data = json.loads(response.text)['data']
        return t_data

    def get_search_index(self):
        print('Cookie:',self.headers['Cookie'][-11:])

########搜索指数
        url = self.search_index_url + urlencode(self.parmas)
        response = requests.get(url, headers=self.headers,verify=False)
        #print(response.text)
        print('message:',json.loads(response.text)['message'])

        if json.loads(response.text)['message'] == 0:
            for info in json.loads(response.text)['data']['userIndexes']:
                #获取get_sign()函数的参数key
                all = info['all']['data']
                pc = info['pc']['data']
                mobile = info['wise']['data']
                endDate = info['all']['endDate']
            total_data = self.fillzero(self.getSign(self.get_parmas(), all).split(','))
            pc_data = self.fillzero(self.getSign(self.get_parmas(), pc).split(','))
            mobile_data = self.fillzero(self.getSign(self.get_parmas(), mobile).split(','))

    #######媒体指数
            url = self.media_index_url + urlencode(self.parmas)
            res = requests.get(url, headers=self.headers,verify=False)

            message = json.loads(res.text)['message']
            #print(message, ':', self.keyword)
            if message == 'success':
                # with open('baidusuccess.txt', 'a+', encoding='utf-8') as f:
                #     f.write(self.keyword)
                #     f.write('\n')

                for i in json.loads(res.text)['data']['index']:
                    newsindex = i['data']
                media_datas = self.fillzero(self.getSign(self.get_parmas(), newsindex).split(','))

        ########资讯指数
                # url = self.resource_url + urlencode(self.parmas)
                # res = requests.get(url, headers=self.headers)
                # for i in json.loads(res.text)['data']['index']:
                #     resource_data = i['data']
                #     if resource_data == '':
                #         resource_datas = [0] * self.day
                #     else:
                #         resource_datas = self.getSign(self.get_parmas(), resource_data).split(',')

        #############
                #for i, (total, pc, mobile,media_index,resource_data) in enumerate(zip(total_data, pc_data, mobile_data,media_datas,resource_datas)):
                for i, (total, pc, mobile, media_index) in enumerate(zip(total_data, pc_data, mobile_data, media_datas)):

                    item = {}
                    item['total'] = self.fillnull(total)
                    item['pc'] = self.fillnull(pc)
                    item['mobile'] = self.fillnull(mobile)
                    item['mediaindex']=self.fillnull(media_index)
                    #item['resourceindex'] = self.fillnull(resource_data)
                    item['keyword'] = self.keyword

        ############按指定日期########
                    timeStamp = int(time.mktime(self.endDate.timetuple())) #将最后一天转成时间戳
                    lastday = timeStamp - 60 * 60 * 24 * (self.time_differ - i) #反推前一天的日期
                    last = time.strftime('%Y-%m-%d', time.localtime(lastday))
        ################

        #########按时间间隔#########
                    # timeArray = time.strptime(endDate, "%Y-%m-%d")
                    # # 转换成时间戳
                    # #print(endDate)
                    # endtimestamp = int(time.mktime(timeArray))*1000
                    # lastday = endtimestamp - 60 * 60 * 24 * (self.day - i-1)*1000
                    # last = time.strftime('%Y-%m-%d', time.localtime(lastday/1000))
        #########################
                    item['day'] = last
                    print(item)
                    #save_csv('baiduindex.csv',item)

        elif 'bad request' in json.loads(response.text)['message']:
            with open('baiduNUll.txt', 'a+', encoding='utf-8') as f:
                f.write(self.keyword)
                f.write('\n')

        else:
            with open('baidu.txt', 'a+', encoding='utf-8') as f:
                f.write(self.keyword)
                f.write('\n')


if __name__ == '__main__':


    def save_csv(filename, data):
        with open(filename, 'a', newline='', errors='ignore', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(data.values())


    #
    # with open('keyword.txt', 'r',
    #           encoding='utf-8-sig') as f:
    #     keywords = f.readlines()

    for i,name in enumerate(keywords):
        keyword = name[0].strip()
        print('keyword:',keyword)
        time.sleep(30)
        api = BaiDuIndex(keyword,COOKIES[i%len(COOKIES)])
        try:
            api.get_search_index()
        except Exception as e:
            print(e)
