# -*- coding: utf-8 -*-
from urllib.parse import urlencode

import scrapy
import re
import pandas as pd

copy_cookie = 'SINAGLOBAL=1458811636830.1707.1549077723302; _s_tentry=login.sina.com.cn; Apache=6548765563491.63.1550731746913; ULV=1550731747033:2:2:1:6548765563491.63.1550731746913:1549077723354; TC-V5-G0=c427b4f7dad4c026ba2b0431d93d839e; TC-Page-G0=9183dd4bc08eff0c7e422b0d2f4eeaec; SSOLoginState=1550828159; Ugrow-G0=e66b2e50a7e7f417f6cc12eec600f517; wvr=6; UOR=,,www.baidu.com; wb_view_log_5264246287=1920*10801; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WW889d9IOyFr2X9x2dfgFS.5JpX5KMhUgL.Fo-ESoBEShqE1hM2dJLoIfQLxKqLBonLBKeLxKqLBo-LB-2LxKnL12-LB-zLxK-L1K5L12BLxK-L1h-LBoeLxKqLBoeLBKnLxKnL12-LB-zLxK-L1K5L12BLxKML1hzLBo.LxKnLBo-L1--t; ALF=1582686106; SCF=AoFkAItovh-b75Fjf0ydy0jxLNCJyjTJIo51czmo_9Lkc3A4Wbkf7Ut8N-1gzWerU7IaZE2QTamAaVoKR4eOuAY.; SUB=_2A25xcNxKDeRhGeNM7VYT9CjOwzuIHXVSBEqCrDV8PUNbmtAKLVTMkW9NThMvEkySFxVV1r4lvhiindpRJF5tOW4X; SUHB=0WGs8Vst-UWu_p; webim_unReadCount=%7B%22time%22%3A1551151463907%2C%22dm_pub_total%22%3A18%2C%22chat_group_pc%22%3A0%2C%22allcountNum%22%3A0%2C%22msgbox%22%3A2%7D'

class transCookie:
    def __init__(self, cookie):
        self.cookie = cookie
    def stringToDict(self):
        '''
        将从浏览器上Copy来的cookie字符串转化为Scrapy能使用的Dict
        :return:
        '''
        itemDict = {}
        items = self.cookie.split(';')

        for item in items:
            key = item.split('=')[0].replace(' ', '')
            value = item.split('=')[1]
            itemDict[key] = value
        return itemDict
def cookiemain():
    trans = transCookie(copy_cookie)
    return trans.stringToDict()

class WeibochaohuaSpider(scrapy.Spider):
    name = 'weibochaohua'
    # allowed_domains = ['weibo.com']
    # start_urls = ['http://weibo.com/']
    start_url='https://s.weibo.com/weibo?q={}&Refer=SWeibo_box'

#######话题###3
    def start_requests(self):
        for keyword in pd.read_excel(r'D:\hulian\Documents\WXWork\1688851171353450\Cache\File\2019-02\青春有你top30-0226.xlsx')['姓名']:
            parmas ={
                'q': '#'+keyword+'青春有你#',
                'wvr': '6',
                'b': '1'
            }
            url = 'https://s.weibo.com/weibo?'+urlencode(parmas)
            yield scrapy.Request(url,meta={'keyword':keyword},callback=self.parse_huati,cookies=cookiemain())
#############

# #########超话#####
#     def start_requests(self):
#         for name in pd.read_excel(r'D:\hulian\Documents\WXWork\1688851171353450\Cache\File\2019-02\青春有你top30-0226.xlsx')['姓名']:
#             if name:
#                 #name = str(re.search('#(.*)#',name).group(1))
#                 print(name)
#                 #name='刘亦菲'
#                 url = self.start_url.format(name)
#                 yield scrapy.Request(url,cookies=cookiemain(),callback=self.parse_chaohuID)
###########
    def parse_chaohuID(self, response):
        chaohua = response.xpath('//i[@class="icon-interest icon-topic-super2"]/../a/@href').extract_first()
        if 'https' in chaohua:
            url = chaohua+'/super_index'
        else:
            url = re.sub('http','https',chaohua)
        yield scrapy.Request(url,callback=self.parse_chaohua,cookies=cookiemain())

    def parse_chaohua(self, response):

        '阅读:174933996492,帖子:8852240,粉丝:4032443'
        item={}
        content = response.xpath('//meta/@content').extract_first()
        #print(content)
        item['name'] = re.search('CONFIG\[\'onick\'\]=\'(.*)\'',response.text).group(1)
        item['read_count'] = re.search('阅读:(\d+),',content).group(1)
        item['tiezi_count'] = re.search('帖子:(\d+),', content).group(1)
        item['fans_count'] = re.search('粉丝:(\d+)', content).group(1)
        yield item

    def parse_huati(self, response):
        item={}
        item['name'] = response.meta['keyword']
        item['read_count'] = self.parseString(response.xpath('//div[@class="total"]/span[1]/text()').re_first('阅读(.*)'))
        item['talk'] = self.parseString(response.xpath('//div[@class="total"]/span[2]/text()').re_first('讨论(.*)'))
        yield item

    def parseString(self, strValue):
        if '万' in strValue:
            data = float(re.sub('万', '', strValue)) * 10000
        elif '亿' in strValue:
            data = float(re.sub('亿', '', strValue)) * 100000000

        else:
            data = int(strValue)
        return round(data)
