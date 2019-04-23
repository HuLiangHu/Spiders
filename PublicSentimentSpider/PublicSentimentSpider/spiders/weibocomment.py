# -*- coding: utf-8 -*-
from urllib.parse import urlencode
import random
import scrapy
import re
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup
from lxml import etree
from pyquery.text import extract_text
import logging

class transCookie:
    def __init__(self, cookie):
        self.cookie = cookie
    def stringToDict(self):
        '''
        将从浏览器上Copy来的cookie字符串转化为Scrapy能使用的Dict
        :return:
        '''
        itemDict = {}
        items = self.cookie[0].split(';')

        for item in items:
            key = item.split('=')[0].replace(' ', '')
            value = item.split('=')[1]
            itemDict[key] = value
        return itemDict
def cookiemain():
    cookies = 'SUB=_2AkMsjJkLf8NxqwJRmP4XxWLrbIlxwwrEieKa0GjQJRMxHRl-yT9jqhwttRB6Bwy35GYG1eqetC6YYrdHYWYeRhg9PQfy; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9Wh2ygIar.anAQ3FwwC6eCbd; SINAGLOBAL=5378646096985.047.1540363794413; UOR=,,www.baidu.com; login_sid_t=791ddd5fef7f445089c3e1baf33862a2; cross_origin_proto=SSL; TC-Ugrow-G0=e66b2e50a7e7f417f6cc12eec600f517; TC-V5-G0=634dc3e071d0bfd86d751caf174d764e; wb_view_log=1920*10801; _s_tentry=www.baidu.com; Apache=1943711391676.1995.1541044833612; ULV=1541044833624:2:1:1:1943711391676.1995.1541044833612:1540363794455; TC-Page-G0=c9fb286cd873ae77f97ce98d19abfb61',
    trans = transCookie(cookies)
    return trans.stringToDict()

class WeibocommentSpider(scrapy.Spider):
    name = 'weibocomment'
   # allowed_domains = ['weibo.com']
    #微博详情页，要抓取微博评论的URL
    start_urls = 'https://weibo.com/2057769762/H1Jro2IM1?type=comment'
    headers ={
        'Host': 'weibo.com',
        'Referer': 'https://weibo.com/5363238224/GFTM6qLBP?filter=hot&root_comment_id=0&type=comment',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }
    commentapi = 'https://weibo.com/aj/v6/comment/big?'
    page = 1

    def start_requests(self):
        yield scrapy.Request(self.start_urls,headers=self.headers,cookies=cookiemain())
    def parse(self, response):
        commentId =re.search('feed&value=comment:(\d+)',response.text).group(1)
        parmas = {
            'ajwvr': '6',
            'id': commentId,
            'from': 'singleWeiBo',
            '__rnd': int(time.time())*1000,
            'sum_comment_number':0
        }
        firstpage = self.commentapi+urlencode(parmas)
        yield scrapy.Request(firstpage,callback=self.parse_nextpage,meta={'parmas':parmas,'page':self.page},cookies=cookiemain())


    # def parse_root_comment_max_id(self,response):
    #     parmas = response.meta['parmas']
    #     data = json.loads(response.text)['data']['html']
    #
    #

    def parse_nextpage(self, response):
        parmas = response.meta['parmas']
        page = response.meta['page']
        last_sum_comment_number = parmas['sum_comment_number']

        data = json.loads(response.text)['data']['html']
        root_comment_max_id = re.search('root_comment_max_id=(\d+)', data)
        root_comment_max_id_type =re.search('root_comment_max_id_type=(\d+)', data)
        sum_comment_number = re.search('sum_comment_number=(\d+)',data)

        #if int(last_sum_comment_number) != int(sum_comment_number.group(1)):
        html = BeautifulSoup(data,'lxml').prettify()
        infos = etree.XML(html)
        item={}
        for info in infos.xpath('//div[@class="list_con"]'):
            author= info.xpath('div[@class="WB_text"]/a/text()')
            item['author'] = re.sub(r'\\n\\n\\n\\n\\n评论配图','',self.fixconten(author)).strip('\\n')
            item['author_home'] ='https:'+info.xpath('div[@class="WB_text"]/a[1]/@href')[0]
            comment = info.xpath('div[@class="WB_text"]/text()')
            item['comment'] = self.fixconten(comment).strip('\\').strip('n\\n：')
            pubtime= info.xpath('div/div[@class="WB_from S_txt2"]/text()')
            item['pubtime'] = self.fixconten(pubtime).strip('\n')
            try:
                reply = info.xpath('div[@class="list_box_in S_bg3"][2]//a[2]/text()')
                item['reply'] = re.search('(\d+)',reply[0]).group(1)
                like =info.xpath('div[@class="WB_func clearfix"]//a[@title="赞"]//em[2]/text()')
                item['like'] = re.search('(\d+)',like[0]).group(1)
            except:
                item['reply'] = 0
                item['like'] =0
            item['crawldata'] = str(datetime.now()).split('.')[0]
            yield item

        try:

            page=page+1
            parmas['page'] =page
            parmas['root_comment_max_id'] = root_comment_max_id.group(1)
            parmas['sum_comment_number'] =sum_comment_number.group(1)
            parmas['root_comment_ext_param'] = ''
            parmas['root_comment_max_id_type'] = root_comment_max_id_type.group(1)
            parmas['__rnd'] = int(time.time()) * 1000 + int(random.randint(300, 1000))
            nextpage = self.commentapi + urlencode(parmas)
            yield scrapy.Request(nextpage, callback=self.parse_nextpage, meta={'parmas': parmas,'page':page}, cookies=cookiemain(),dont_filter=False)
        except:
            print('GoodJob!!!')

    def fixconten(self,string):
        content = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——#￥%……&*（）]+", "", str(string).strip())
        data = re.search('\\\\n(.*)\\\\n',content).group(1)
        return data


