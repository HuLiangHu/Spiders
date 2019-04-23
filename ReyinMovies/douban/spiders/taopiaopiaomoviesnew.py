# -*- coding: utf-8 -*-
from datetime import datetime

import scrapy
import time
import json
from urllib.parse import urlencode
import re
import execjs
import http.cookiejar,urllib.request
# import ssl
#
# ssl._create_default_https_context = ssl._create_unverified_context



class TaopiaopiaomoviesnewSpider(scrapy.Spider):
    name = 'taopiaopiaomoviesnew'
    # allowed_domains = ['taopiao.com']
    # start_urls = ['http://taopiao.com/']
    #app = '57aea0814c75d8a700f7c83f30230482_1539968131183'
    appkey = '12574478'
    movielisturl ='https://acs.m.taopiaopiao.com/h5/mtop.film.mtopshowapi.getextendshowbyid/5.4/?jsv=2.4.16&appKey=12574478&t=1540261776801&sign=0bb2cb6704fd82d05b4e0bbfee21afa9&api=mtop.film.MtopShowAPI.getExtendShowById&v=5.4&timeout=10000&forceAntiCreep=true&AntiCreep=true&type=jsonp&dataType=jsonp&callback=mtopjsonp1&data=%7B%22showid%22%3A%22525339%22%2C%22cityCode%22%3A%22310100%22%2C%22platform%22%3A%228%22%7D'

    data = {
        "field": "i:id;poster;showName;showMark;remark;preScheduleRemark;director;leadingRole;previewNum;openDay;openTime;wantCount;fantastic;specialSchedules(i:id;tag;title;description)-1;derivationList(i:id;label;title;links;advertiseType);activities(i:id;activityTag;activityExtType;activityTitle;longDescription);type;duration;country;openCountry;friendCount;friends;starMeeting;preScheduleDates;soldTitle;soldType",
        "pageIndex": 1, "pagesize": 10, "citycode": "310100", "pageCode": "", "platform": "8"}

    def getSign(self,str):

        with open("douban/taopiao.js", encoding='utf-8') as f:
            jsData = f.read()
        js = execjs.compile(jsData)
        sign = js.call('c', str)
        return sign

    def getCookie(self,url):
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

    # def getdetailinfoCookie(self,url):
    #     cookies = http.cookiejar.CookieJar()
    #     handler = urllib.request.HTTPCookieProcessor(cookies)
    #     opener = urllib.request.build_opener(handler)
    #     response = opener.open(url)
    #     cookiestr = ""
    #     for cookie in cookies:
    #         cookie_name = cookie.name
    #         cookie_value = cookie.value
    #         cookiestr = cookiestr + cookie_name + '=' + cookie_value + '; '
    #     return cookiestr

    def start_requests(self):
        timestame = int(time.time() * 1000)
        # self.data['pageIndex'] = 1
        cookies = self.getCookie(self.movielisturl)

        app = re.search('_m_h5_tk=(.*?);', cookies).group(1)
        app = app.split('_')[0]
        for page in range(1,10):
            self.data['pageIndex']=page
            canshu = app + '&' + str(timestame) + '&' + self.appkey + '&' + str(self.data)
            sign = self.getSign(canshu)

            baseurls = ['https://acs.m.taopiaopiao.com/h5/mtop.film.mtopshowapi.getshowsbycitycode/4.0/?',
                        'https://acs.m.taopiaopiao.com/h5/mtop.film.mtopshowapi.getsoonshowsbycitycode/5.0/?']


            headers = {
                #'cookie': 'cna=PY3IE9A6dD8CAd+m53u4/s92; new_pkg=no; t=1922190c23706744f0fd53a3ddfb297f; lid=%E6%B7%98%E5%87%BA%E6%88%91%E7%9A%84%E6%97%B6%E5%B0%9Ahl; _tb_token_=f165eebe89538; cookie2=1ab9ea73fcf3648c47d149971104c816; _m_h5_tk=57aea0814c75d8a700f7c83f30230482_1539968131183; _m_h5_tk_enc=2802da84f5210803d6fa57e164e5d853; isg=BOHh2doLHnkD37K24qBf_2CC8Ks7JlSGyP3PnEO23ehHqgF8i95lUA_sCJiJPe24',
                'cookie':cookies,
                # 'referer': 'https://h5.m.taopiaopiao.com/app/moviemain/pages/index/index.html?from=outer&spm=a1z21.6646385.header.3.614e2c47Ql6p6T&n_s=new',
                'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
            }
            parmas = {
                'jsv': '2.4.16',
                'appKey': '12574478',
                't': timestame,
                'sign': sign,
                'v': '5.0',
                'timeout': '10000',
                'forceAntiCreep': 'true',
                'AntiCreep': 'true',
                'dataType': 'jsonp',
                'data': self.data
            }

            url = baseurls[0] + urlencode(parmas)
            headers['referer'] = url
            yield scrapy.Request(url,headers=headers,cookies=cookies,meta={'dont_merge_cookies': True,'cookies':cookies})
        comingurl =baseurls[1]+urlencode(parmas)
        yield scrapy.Request(comingurl,headers=headers,meta={'dont_merge_cookies': True,'cookies':cookies})

    def parse(self, response):

        t = int(time.time() * 1000)

        for info in json.loads(response.text)['data']['returnValue']:
            item = {}
            item['name'] = info['showName']
            item['movieDate'] = str(info['openDay']).split(' ')[0]
            item["comefrom"] = "淘票票"
            item["filmid"] = info['id']
            item['want'] = info['wantCount']
            try:
                try:
                    item['Grade'] = info['preScheduleRemark']
                except:
                    item['Grade'] = info['remark']
            except:
                item['Grade'] = None

            item['crawldate'] = str(datetime.today())
            item["createdtime"] = str(datetime.now())

            app = re.search('_m_h5_tk=(.*?);', response.meta['cookies']).group(1)
            app = app.split('_')[0]
            gradedata = {"showid": "", "cityCode": "310100", "platform": "8"}
            gradedata['showid'] =item["filmid"]
            canshu = app + '&' + str(t) + '&' + self.appkey + '&' + str(gradedata)
            sign = self.getSign(canshu)
            parmas = {
                'jsv': '2.4.16',
                'appKey': '12574478',
                't': t,
                'sign': sign,
                'expire_time': '180000',
                'timeout': '10000',
                'forceAntiCreep': 'true',
                'AntiCreep': 'true',
                'dataType': 'jsonp',
                'data': gradedata
            }
            #
            url = 'https://acs.m.taopiaopiao.com/h5/mtop.film.mtopshowapi.getextendshowbyid/5.4/?' + urlencode(parmas)
            headers = {
                'cookie': response.meta['cookies'],
                'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
            }
            yield scrapy.Request(url,callback=self.parse_gradepeople,headers=headers,cookies=response.meta['cookies'],meta={'dont_merge_cookies': True,'item':item})

    def parse_gradepeople(self, response):
        info = json.loads(response.text)
        item = response.meta['item']
        try:
            try:
                item['gradePeople'] = info['data']['returnValue']['remarkCount']
            except KeyError:
                item['gradePeople']= info['data']['returnValue']['preScheduleRemarkCount']
        except:
            item['gradePeople'] =None
        yield item