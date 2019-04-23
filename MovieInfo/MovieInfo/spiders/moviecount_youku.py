# -*- coding: utf-8 -*-
import http
import time
import urllib
from urllib.parse import urlencode

import execjs
import scrapy
import json
import re
from scrapy.selector import Selector
from datetime import datetime
from MovieInfo.items import MoviecountsItem

from lxml import etree
import requests
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
def cookiemain(cookies):
    #cookies='_m_h5_tk=ae4911818b19ee7702161cab577ed913_1550038229549; _m_h5_tk_enc=f83a8067478811c716db348bba306e61'
    trans = transCookie(cookies)
    return trans.stringToDict()

def get_comingmoviename():
    doubanwill = 'https://movie.douban.com/coming'
    res = requests.get(doubanwill,verify=False).text
    html = etree.HTML(res)
    name = html.xpath('//div[@class="grid-16-8 clearfix"]/div/table/tbody/tr/td/a/text()')
    return name

class YoukuSpider(scrapy.Spider):

    name = "moviecount_youku"
    moviename=get_comingmoviename()
    starturls = 'https://so.youku.com/search_video/q_{}?spm=a2h0k.11417342.filter.dcategory&categories=96'
    dataapi='http://ykrec.youku.com/show/packed/list.json?guid=1473252441267REV&utdid=WfpWELna+jECATrTRuOH/yBR&sid={}&cate=96&picSize=2&apptype=1&pg=3&module=9&pl=18&needTags=1&atrEnable=true'
    def start_requests(self):
        # self.server = connection.from_settings(self.settings)
        for name in self.moviename:#self.moviename:
            url = self.starturls.format(name)
            yield scrapy.Request(url,callback=self.parse_all_prevues,meta={"name":name})

    def parse_all_prevues(self,response):
        try:
            prevues_list_url = re.search('(list.youku.com/show/id_.*?.html)',response.text).group(1)
            url = 'https://'+prevues_list_url
            yield scrapy.Request(url,callback=self.parse_showId,meta={"name":response.meta['name']})
        except:
            self.log('没有找到电影:{} 相关信息'.format(response.meta['name']))
    def parse_showId(self,response):
        showId = re.search('showid:"(\d+)"',response.text).group(1)
        url ='https://list.youku.com/show/module?id={}&tab=around_2&cname=%E7%94%B5%E5%BD%B1&callback=jQuery'.format(showId)
        yield scrapy.Request(url,callback=self.parse_item,meta={"name":response.meta['name']})


    def parse_item(self, response):
        name = response.meta['name']
        try:
            item = MoviecountsItem()
            item["comefrom"] = "youku"
            item["datetime"] = str(datetime.now())
            infos1 = re.findall('id_(.*?)==.html.*?">(.*?)</a>', response.text)
            infos2 = re.findall(r'id_(.*?)==.html.*?>(.*?)<\\/a>', response.text)
            if infos1 == []:
                infos = infos2
            else:
                infos = infos1
            for i in infos:
                if i[1]:
                    videoid = i[0]
                    item['title'] = i[1].encode('utf8').decode('unicode_escape')
                    item["url"]='https://v.youku.com/v_show/id_{}'.format(videoid)
                    url = 'https://m.youku.com/video/id_{}?source='.format(videoid)
                    header = {
                        'Host': 'm.youku.com',
                        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
                    }
                    yield scrapy.Request(url, callback=self.parse_playcount, meta={'item': item, 'videoid': videoid},
                                         headers=header)
        except:
            self.log('没有找到电影:{} 预告片'.format(name))

    def parse_playcount(self, response):
        #print(response.text)
        try:
            item = response.meta['item']
            item['view_count'] = re.search('热度 (.*?)\"', response.text).group(1)
            yield item
        except:
            tvplay = response.meta['item']
            vid = response.meta['videoid']
            a = int(time.time() * 1000)
            cookie = self.getCookie(
                'https://acs.youku.com/h5/mtop.youku.haixing.play.h5.detail/1.0/?appKey=24679788&t=1550038676898&sign=74847a987adb4e069f845c672a1cc27e&v=1.0&type=originaljson&dataType=json&api=mtop.youku.haixing.play.h5.detail')[
                     :-2]
            # print(cookie)
            # cookie='_m_h5_tk=ae4911818b19ee7702161cab577ed913_1550038229549; _m_h5_tk_enc=f83a8067478811c716db348bba306e61'
            headers = {
                'Cookie': cookie,
                'Host': 'acs.youku.com',
                'Origin': 'https://m.youku.com',
                'Referer': 'https://m.youku.com/video/id_XMzk4MDUzNTA1Mg==.html?spm=a2h1n.8261147.reload_1.1~3~A&s=66efbfbd65efbfbd3919&source=http%3A%2F%2Fv.youku.com%2Fv_show%2Fid_XMzk4MDUzNTA1Mg%3D%3D.html%3Fspm%3Da2h1n.8261147.reload_1.1~3~A%26s%3D66efbfbd65efbfbd3919',
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
            }

            # print(a)
            token = str(re.search('_m_h5_tk=(.*?);', cookie).group(1)).split('_')[0]
            n = {"device": "H5", "layout_ver": "100000",
                 "system_info": "{\"device\":\"H5\",\"pid\":\"69b81504767483cf\",\"guid\":\"15490097626395dE\",\"utdid\":\"15490097626395dE\",\"ver\":\"1.0.0.0\",\"userAgent\":\"Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1\"}"}
            n['video_id'] = vid
            n = json.dumps(n)
            appkey = '24679788'
            # print(n)
            parmas = r'{0}&{1}&{2}&{3}'.format(token, a, appkey, n)
            sign = self.getSign(parmas)
            # print(sign)
            data = {
                'data': n
            }
            p = {
                'appKey': '24679788',
                't': a,
                'sign': sign,
                'v': '1.0',
                'type': 'originaljson',
                'dataType': 'json',
                'api': 'mtop.youku.haixing.play.h5.detail'
            }
            url = 'https://acs.youku.com/h5/mtop.youku.haixing.play.h5.detail/1.0/?' + urlencode(p)
            # cookie=self.getCookie(url)
            yield scrapy.FormRequest(url, formdata=data, headers=headers, callback=self.parse_extraplaycount,
                                     meta={'tvplay': tvplay}, cookies=cookiemain(cookie))

    def parse_extraplaycount(self, response):
        tvplay = response.meta['tvplay']
        # print(response.text)
        for i in json.loads(response.text)['data']['moduleResult']['modules']:
            for j in i['components']:
                try:
                    if tvplay['title'] in j['itemResult']['item']['1']['title']:
                        tvplay['view_count'] = j['itemResult']['item']['1']['totalVv']
                        # print(tvplay)
                        yield tvplay
                except:
                    pass

    def getSign(self, parmas):
        with open("webplay/youku.js") as f:
            jsData = f.read()

        js = execjs.compile(jsData)
        sign = js.call('sign', parmas)
        return sign

    def getCookie(self, url):
        cookies = http.cookiejar.CookieJar()
        handler = urllib.request.HTTPCookieProcessor(cookies)
        opener = urllib.request.build_opener(handler)
        response = opener.open(url)
        cookiestr = ""
        for cookie in cookies:
            cookie_name = cookie.name
            cookie_value = cookie.value
            cookiestr = cookiestr + cookie_name + '=' + cookie_value + '; '
        return cookiestr











