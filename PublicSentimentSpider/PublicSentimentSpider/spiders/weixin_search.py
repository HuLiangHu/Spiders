# -*- coding: utf-8 -*-
import scrapy
import time
from urllib.parse import urlencode
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
    cookies = 'IPLOC=CN3100;SUID=0EA8233A2C12960A000000005BD2A99E;SUV=1540532590570839;sct=1;SNUID=06A02B33080C70133DD910A40925163A;ld=Zkllllllll2b1$uelllllVsv$b9lllllnAnoRkllll9lllllpklll5@@@@@@@@@@;LSTMV=245%2C157;LCLKINT=3526;ABTEST=7|1540532668|v1;JSESSIONID=aaaOMYLARPXHpauw4ELzw'
    trans = transCookie(cookies)
    return trans.stringToDict()

class WeixinSpider(scrapy.Spider):
    name = 'weixin_search'
    #allowed_domains = ['weixin.com']
    #start_urls = 'http://v.qq.com/detail/1/1wbx6hb4d3icse8.html'
    keyword = "i黑马"
    baseurl = 'https://weixin.sogou.com/weixin?'

    headers ={
        'Host': 'weixin.sogou.com',
        'Referer': 'https://weixin.sogou.com/weixin?type=2&ie=utf8&query=i%E9%BB%91%E9%A9%AC&tsn=4&ft=&et=&interation=&wxid=&usip=',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }
    def start_requests(self):
        cookies = cookiemain()
        for page in range(1,2):
            parmas ={
                'usip':'',
                'query':self.keyword,
                'ft':'',
                'tsn':'4',
                'et':'',
                'interation':'',
                'type':'2',
                'wxid':'',
                'page':page,
                'ie':'utf8'
            }
            url =self.baseurl+urlencode(parmas)

            yield scrapy.Request(url,headers=self.headers,cookies=cookies)

    def parse(self, response):

        for info in response.xpath('//div[@class="txt-box"]'):
            item={}
            item['title'] = info.xpath('string(h3/a)').extract_first()
            item['content'] =info.xpath('string(p[@class="txt-info"])').extract_first()
            item['name'] =info.xpath('div[@class="s-p"]/a/text()').extract_first()
            pubtime=info.xpath('div[@class="s-p"]/@t').extract_first()
            item['pubtime'] =time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(pubtime)))

            yield item