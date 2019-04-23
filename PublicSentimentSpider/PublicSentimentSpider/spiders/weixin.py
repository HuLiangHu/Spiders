# -*- coding: utf-8 -*-
import scrapy
import json

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
    cookies = 'devicetype=iOS12.0.1; lang=zh_CN; pass_ticket=I59z0zeErCT8Ldz4PAaTBjAZmyn/HRSwtyaYs9Fw94jAMCN6W5ocBbWWplgAGZnK; version=16070322; wap_sid2=CMO8+9QKElwxUG50dDVkMkRmLThLRnZySUhfbXJwbDVaU0dTYnF6dTZfOEJQbGJfRm9UaGtaMnZhaEVXOGVOSnNBMmFyQWhfdHVQb3VVUm9TZzNnZ3JQcEFWTGRvOVFEQUFBfjD9hsveBTgNQJVO; wxuin=2862538307; wxtokenkey=777; rewardsn='
    trans = transCookie(cookies)
    return trans.stringToDict()

class WeixinSpider(scrapy.Spider):
    name = 'weixin'
    # allowed_domains = ['weixin.com']
    start_urls = 'https://mp.weixin.qq.com/mp/profile_ext?action=getmsg&__biz=MzA3MDM3MDYwMg==&f=json&offset={}&count=10&is_ok=1&scene=126&uin=777&key=777&pass_ticket=I59z0zeErCT8Ldz4PAaTBjAZmyn%2FHRSwtyaYs9Fw94jAMCN6W5ocBbWWplgAGZnK&wxtoken=&appmsg_token=980_Cepw0GFewwioSRiZmeTAkwOVjxqF5WfR3f_PTw~~&x5=0&f=json'
    keyword =''
    headers = {
        'Host': 'mp.weixin.qq.com',
        #'Cookie': 'devicetype=iOS12.0.1; lang=zh_CN; pass_ticket=I59z0zeErCT8Ldz4PAaTBjAZmyn/HRSwtyaYs9Fw94jAMCN6W5ocBbWWplgAGZnK; version=16070322; wap_sid2=CMO8+9QKElwxUG50dDVkMkRmLThLRnZySUhfbXJwbDVaU0dTYnF6dTZfOEJQbGJfRm9UaGtaMnZhaEVXOGVOSnNBMmFyQWhfdHVQb3VVUm9TZzNnZ3JQcEFWTGRvOVFEQUFBfjD9hsveBTgNQJVO; wxuin=2862538307; wxtokenkey=777; rewardsn=',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16A404 MicroMessenger/6.7.3(0x16070321) NetType/WIFI Language/zh_CN'
    }
    def start_requests(self):
        for page in range(1,2):
            url = self.start_urls.format(str(page*10))
            yield scrapy.Request(url,headers=self.headers,cookies=cookiemain())

    def parse(self, response):
        #print(json.loads(response.text)['general_msg_list'])
        for info in json.loads(json.loads(response.text)['general_msg_list'])['list']:
            # print(info)
            item = {}
            item['tilte'] = info['app_msg_ext_info']['title']
            item['subscripition'] = self.keyword
            #item['content'] = info['app_msg_ext_info']['content']
            item['url'] = info['app_msg_ext_info']['content_url']

            yield item
            for i in info['app_msg_ext_info']['multi_app_msg_item_list']:
                citem = {}
                citem['title'] = i['title']
                item['subscripition'] = self.keyword
                #citem['content'] = i['content']
                citem['url'] = i['content_url']

                yield citem

