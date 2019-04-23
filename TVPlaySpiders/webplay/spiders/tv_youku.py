# -*- coding: utf-8 -*-
import time
from urllib.parse import urlencode
import http.cookiejar,urllib.request
import execjs

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


import scrapy
from datetime import datetime
import json
import re
from random import choice
from webplay.items import TVPlayItem
'''
###接口失效后直接爬取网页内容
#http://api.mobile.youku.com/layout/android5_0/play/detail?pid=bb2388e929bc3038&guid=8cf328de53f363c2be6b43a5cb2511c2&format=&id=0a007a10e9c211e5b522&area_code=1
#'http://api.mobile.youku.com/layout/v_5/android/channel/subpage?pid=bb2388e929bc3038&guid=8cf328de53f363c2be6b43a5cb2511c2&cid=97&sub_channel_id=1&sub_channel_type=4&filter=&ob=2&pg=1',
class YoukuSpider(scrapy.Spider):
    name = "tv_youku"
    CLIENT_IDS = ['601a5d6a43a8b0f4','d68017cf81224349','70ecad56b9804e77']
    MAX_COUNT = 1500
    cookies = {'sec':'58aba876b30e38f721c189435e44dcac996ae2c3', 'ykss':'76a8ab58cc822bdaebb219fe'}
    custom_settings = {
        "DOWNLOAD_DELAY" : 1
    }

    start_urls = [ 'https://list.youku.com/category/show/c_97_u_1_s_1_d_1_p_1.html?spm=a2h1n.8251845.0.0',
                  'https://list.youku.com/category/show/c_97_u_2_s_1_d_1_p_1.html?spm=a2h1n.8251845.filterPanel.5!5~1~3!3~A',
                  'https://list.youku.com/category/show/c_97_u_4_s_1_d_1_p_1.html?spm=a2h1n.8251845.filterPanel.5!5~1~3!5~A'
                  ] 
    
    def parse(self,response):
        
        page_nums = response.xpath('//div[@class="yk-pager"]/ul/li/a/text()').extract()
        if len(page_nums)>0:
            page_num = page_nums[-2]
            for i in range(1, int(page_num) + 1):
                next_listurl = response.url.replace('p_1', 'p_' + str(i))
                yield scrapy.Request(next_listurl, callback=self.parse_movieid)
        
        url = response.url
        yield scrapy.Request(url,callback=self.parse_movieid,priority=2, dont_filter=True)
    def parse_movieid(self,response):
        next_urls = response.xpath('//div[@class="vaule_main"]/div[@class="box-series"]/ul/li/div/div/a/@href').extract()
        for url in next_urls:
            if url.startswith("//list"):
                yield scrapy.Request('https:'+url,priority=4,callback=self.parse_detail)
            if url.startswith("https"):
                yield scrapy.Request(url,priority=3, callback=self.parse_detail_url)
            yield scrapy.Request('https:'+url.strip("https:"),priority=3,callback=self.parse_detail_url)

    def parse_detail_url(self,response):
        detail_url = response.xpath('//div[@class="tvinfo"]/h2/a/@href').extract_first()
        yield scrapy.Request('https:'+str(detail_url),priority=4,callback=self.parse_detail)

    def parse_detail(self,response):
        tvplay=TVPlayItem()
        tvplay["website"] = 'youku'
        tvplay["url"] =  response.url.replace('list.youku.com/show/','www.youku.com/show_page/')
        tvplay["cover_img"] = response.xpath('//div[@class="mod fix"]/div/div/div[@class="p-thumb"]/img/@src').extract_first()
        tvplay["alias"] = response.xpath('//div[@class="p-base"]/ul/li[@class="p-alias"]/@title').extract_first()
        tvplay["area"] = response.xpath('//div[@class="p-base"]/ul/li[9]/a/text()').extract_first()
        tvplay["aid"] =re.findall(r'id_(.*).html',response.url)[0]
        tvplay["directors"] = response.xpath('//div[@class="p-base"]/ul/li[8]/a/text()').extract_first()
        tvplay["actors"] = " ".join(response.xpath('//div[@class="p-base"]/ul/li[7]/a/text()').extract())
        tvplay["playStatus"]=response.xpath('//div[@class="p-base"]/ul/li[@class="p-row p-renew"]/text()').extract_first()
        tvplay["releaseDate"] = response.xpath('//div[@class="p-base"]/ul/li[5]/span/text()').extract_first()
        tvplay["releaseDate"] =response.xpath('//div[@class="p-base"]/ul/li[4]/span/text()').extract_first() #节目发行时间
        tvplay["genre"] = " ".join(response.xpath('//div[@class="p-base"]/ul/li[10]/a/text()').extract())
        tvplay["desc"] = response.xpath('//div[@class="p-base"]/ul/li[@class="p-row p-intro"]/span[@class="text"]/text()').extract_first()
        tvplay["name"] = response.xpath('//div[@class="p-base"]/ul/li[@class="p-row p-title"]/text()').extract_first()[1:]
        tvplay["playdate"] = str(datetime.today())
        
        tvplay['playCount'] = re.search(u'总播放数：([\d,]+)',response.body_as_unicode()).group(1).replace(',','')
        return tvplay



'''
class YoukuSpider(scrapy.Spider):
    name = "tv_youku"

    CLIENT_IDS = ['601a5d6a43a8b0f4' ,'d68017cf81224349' ,'70ecad56b9804e77']
    MAX_COUNT = 1500
    cookies = {'sec' :'58aba876b30e38f721c189435e44dcac996ae2c3', 'ykss' :'76a8ab58cc822bdaebb219fe'}
    custom_settings = {
        "DOWNLOAD_DELAY" : 0.5
    }
    start_urls = [ 
       'https://list.youku.com/show/id_z88f2766bf54748b2b29a.html',
    'https://list.youku.com/show/id_z40da0b961bee49b4ab52.html',
    'https://list.youku.com/show/id_zefbfbd26777fefbfbdef.html',
    'http://list.youku.com/category/show/c_97_a__s_1_d_1.html',
    'https://list.youku.com/show/id_zefbfbd074f62362f11e7.html',
    'https://list.youku.com/show/id_z2348efbfbd0befbfbdef.html',
    'https://list.youku.com/show/id_zd88efd308ea811e69e06.html',
    'https://list.youku.com/show/id_z8384325b8e9411e69e06.html',
    'https://list.youku.com/show/id_z4498d561d2db4d7ea9c6.html'
    'http://list.youku.com/show/id_z66efbfbd65efbfbd3919.html?tpa=dW5pb25faWQ9MTAzNzUzXzEwMDAwMV8wMV8wMQ&refer=baiduald1705'
    ]
    
    def __init__(self):
        super(YoukuSpider ,self).__init__()
        genres = ['言情', '时装', '都市', '剧情', '家庭', '古装', '搞笑', '偶像', '警匪', '历史', '军事', '武侠', '科幻', '农村', '神话', '儿童'
            , '优酷出品', '奇幻', '爱情', '网剧'
                  ]
        for genre in genres:
            self.start_urls.append \
                ( 'https://openapi.youku.com/v2/shows/by_category.json?client_id=%s&category=电视剧&orderby=updated&count=20&page=1&genre=%s' %
                (choice(self.CLIENT_IDS) ,genre))
        
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, cookies=self.cookies)

    def parse(self, response):
        if re.match('^(http|https|ftp)\:\/\/list.youku.com\/category\/show\/.*' ,response.url):
            item_urls = response.xpath('//ul[@class="panel"]/li/div/div/a/@href').extract()
            show_ids = []
            for url in item_urls:
                yield scrapy.Request("https:"+url, callback=self.parse, priority=1)
        elif re.match('^(http|https|ftp)\:\/\/v.youku.com\/v_show\/.*' ,response.url):
            show_id = re.search("showid_en: '([a-zA-Z0-9]+)',",response.body_as_unicode()).group(1)
            yield scrapy.Request('https://openapi.youku.com/v2/shows/show_batch.json?client_id=%s&show_ids=%s' % (
            choice(self.CLIENT_IDS), show_id), callback=self.detail_parse, priority=2, dont_filter=False)
        elif re.match('^(http|https|ftp)\:\/\/openapi.youku.com\/v2\/shows\/by_category.json.*' ,response.url):
            jsonObj = json.loads(response.body_as_unicode())
            if re.search('page=1&' ,response.url):
                page_size = int(re.search('count=(\d+)' ,response.url).group(1))
                total_count = int(jsonObj['total']) if int(jsonObj['total'] ) <self.MAX_COUNT else self.MAX_COUNT
                page_count = int(total_count/ page_size if total_count % page_size == 0 else total_count / page_size + 1)
                for page in range(2, page_count + 1):
                    url = re.sub('page=1&', 'page=%d&' % page, response.url)
                    yield scrapy.Request(url, dont_filter=False)
            show_ids = []

            for item in jsonObj['shows']:
                show_ids.append(item['id'])
            if len(show_ids) > 0:
                yield scrapy.Request('https://openapi.youku.com/v2/shows/show_batch.json?client_id=%s&show_ids=%s' % (
                choice(self.CLIENT_IDS), ','.join(show_ids)), callback=self.detail_parse, priority=1, dont_filter=False)
        else:
            aid = re.search('id_\w(\w+).html', response.url).group(1)
            #playcount = re.search(u'<li>总播放数：([\d,]+)</li>', response.body_as_unicode()).group(1).replace(',', '')
            yield scrapy.Request('https://openapi.youku.com/v2/shows/show_batch.json?client_id=%s&show_ids=%s' % (
            choice(self.CLIENT_IDS), aid), callback=self.detail_parse, priority=2, dont_filter=False)

    def detail_parse(self, response):
        jsonObj = json.loads(response.body_as_unicode())

        for item in jsonObj['shows']:
            director = ''
            actors = ''
            if item['attr']['director']:
                director = ','.join([pers['name'] for pers in item['attr']['director']])
            if item['attr']['performer']:
                actors = ','.join([pers['name'] for pers in item['attr']['performer']])
            tvplay = TVPlayItem()
            tvplay["website"] = 'youku'
            tvplay["url"] = item['link'].replace('http:','https:')
            tvplay["alias"] = item['subtitle']
            tvplay["cover_img_sm"] = item['poster']
            tvplay["cover_img"] = item['poster_large']
            tvplay["area"] = item['area']
            tvplay["aid"] = item['id']
            tvplay["directors"] = director
            tvplay["actors"] = actors
            tvplay["episodes"] = item['episode_count']
            tvplay["playStatus"] = item['update_notice']
            tvplay["releaseDate"] = item['published']  # youku上线时间
            # tvplay["releaseDate"] = item['released'], #节目发行时间
            tvplay["genre"] = item['genre']
            # "tag"] = item['albumDocInfo']['albumTitle'],
            tvplay["desc"] = item['description']
            tvplay["name"] = item['name']
            # api不更新了
            # tvplay["playCount"] = item['view_count']
            # "videoType"] = item['category']
            tvplay["additional_infos"] = {"up_count": item['up_count'],
                                          "down_count": item['down_count'], "favorite_count": item['favorite_count'],
                                          "douban_num": item['douban_num'], "comment_count": item['comment_count']}
            tvplay["playdate"] = str(datetime.today())

            # yield tvplay
            if response.meta and 'playcount' in response.meta:
                tvplay["playCount"] = response.meta['playcount']
                yield tvplay
            else:
                req = scrapy.Request(tvplay["url"], callback=self.playcount_parse,dont_filter=True)
                req.meta['tvitem'] = tvplay
                yield req

    # <li>总播放数：5,321,600,935</li>
    def playcount_parse(self, response):
        tvplay = response.meta['tvitem']
        mainURL = response.xpath('//div[@class="p-thumb"]/a/@href').extract_first()
        videoid = re.search(r'id_(.*).html',mainURL).group(1)
        url = 'https://m.youku.com/video/id_{}?source='.format(videoid)
        header ={
            'Host': 'm.youku.com',
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
        }
        yield scrapy.Request(url,callback=self.parse_playcount,meta={'tvplay':tvplay,'videoid':videoid},headers=header)
        # print(playcount)
    def parse_playcount(self,response):
        try:
            tvplay = response.meta['tvplay']
            tvplay['playCount'] =0
            tvplay['renqi']=re.search('热度 (.*?)\"',response.text).group(1)
            yield tvplay
        except:
            tvplay = response.meta['tvplay']
            tvplay['playCount'] = 0
            vid = response.meta['videoid']
            a = int(time.time() * 1000)
            cookie =self.getCookie('https://acs.youku.com/h5/mtop.youku.haixing.play.h5.detail/1.0/?appKey=24679788&t=1550038676898&sign=74847a987adb4e069f845c672a1cc27e&v=1.0&type=originaljson&dataType=json&api=mtop.youku.haixing.play.h5.detail')[:-2]
            #print(cookie)
            #cookie='_m_h5_tk=ae4911818b19ee7702161cab577ed913_1550038229549; _m_h5_tk_enc=f83a8067478811c716db348bba306e61'
            headers = {
                'Cookie': cookie,
                'Host': 'acs.youku.com',
                'Origin': 'https://m.youku.com',
                'Referer': 'https://m.youku.com/video/id_XMzk4MDUzNTA1Mg==.html?spm=a2h1n.8261147.reload_1.1~3~A&s=66efbfbd65efbfbd3919&source=http%3A%2F%2Fv.youku.com%2Fv_show%2Fid_XMzk4MDUzNTA1Mg%3D%3D.html%3Fspm%3Da2h1n.8261147.reload_1.1~3~A%26s%3D66efbfbd65efbfbd3919',
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
            }

            #print(a)
            token = str(re.search('_m_h5_tk=(.*?);',cookie).group(1)).split('_')[0]
            n = {"device": "H5", "layout_ver": "100000",
                 "system_info": "{\"device\":\"H5\",\"pid\":\"69b81504767483cf\",\"guid\":\"15490097626395dE\",\"utdid\":\"15490097626395dE\",\"ver\":\"1.0.0.0\",\"userAgent\":\"Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1\"}"}
            n['video_id'] = vid
            n = json.dumps(n)
            appkey ='24679788'
            #print(n)
            parmas = r'{0}&{1}&{2}&{3}'.format(token, a, appkey,n)
            sign = self.getSign(parmas)
            #print(sign)
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
            url ='https://acs.youku.com/h5/mtop.youku.haixing.play.h5.detail/1.0/?'+urlencode(p)
            #cookie=self.getCookie(url)
            yield scrapy.FormRequest(url,formdata=data,headers=headers,callback=self.parse_extraplaycount,meta={'tvplay':tvplay},cookies=cookiemain(cookie))

    def parse_extraplaycount(self, response):
        tvplay = response.meta['tvplay']
        #print(response.text)
        for i in json.loads(response.text)['data']['moduleResult']['modules']:
            for j in i['components']:
                try:
                    if tvplay['name'] in j['itemResult']['item']['1']['title']:
                        tvplay['renqi'] = j['itemResult']['item']['1']['totalVv']
                        #print(tvplay)
                        yield tvplay
                except:
                    pass

    def getSign(self,parmas):
        with open("webplay/youku.js") as f:
            jsData = f.read()

        js = execjs.compile(jsData)
        sign = js.call('sign', parmas)
        return sign
        #token ="23fb357c0c29dcb6b78f7c0234739f9c"

        #o="24679788"

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


