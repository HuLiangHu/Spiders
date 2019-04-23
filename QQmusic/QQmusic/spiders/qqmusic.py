# -*- coding: utf-8 -*-
import re
from urllib.parse import urlencode

import scrapy
import json
import time
class QqmusicSpider(scrapy.Spider):
    name = 'qqmusic'
    allowed_domains = ['qq.com']
    start_urls = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_toplist_cp.fcg?'#热歌榜
    renqi_url ='https://c.y.qq.com/rsc/fcgi-bin/fcg_global_gift_rank_list.fcg?'#人气榜
    custom_settings = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    }
#########人气榜###########
    # def start_requests(self):
    #     for year in range(2018,2020):
    #         for week in range(52):
    #             parmas ={
    #                 'g_tk': '5381',
    #                 'uin': '0',
    #                 'format': 'json',
    #                 'inCharset': 'utf-8',
    #                 'outCharset': 'utf-8',
    #                 'notice': '0',
    #                 'platform': 'h5',
    #                 'needNewCode': '1',
    #                 'reqtype': '2',
    #                 'weeklist': '0',
    #                 'year': year,
    #                 'week': week,
    #                 '_': int(time.time()*1000),
    #             }
    #             url = self.renqi_url + urlencode(parmas)
    #             yield scrapy.Request(url, meta={'week': week,'year':year})
    # def parse(self, response):
    #     for i in json.loads(response.text)['data']['ranklist']:
    #         item={}
    #         item['albumdesc'] =i['songinfo']['albumdesc']
    #         item['albumid'] = i['songinfo']['albumid']
    #         item['albumname'] = i['songinfo']['albumname']
    #         item['songname']= i['songinfo']['songname']
    #         interval = i['songinfo']['interval']
    #         item['interval'] = str(int(int(interval / 60))) + '分' + str(int(int(interval % 60)))
    #         item['rank'] = i['rank']
    #         item['renqi']=i['giftvalue']
    #         item['singer'] = [name['name'] for name in i['songinfo']['singer']][0]
    #         item['last_rank'] = i['last_rank']
    #         item['rate']=i['songinfo']['rate']
    #         item['year'] =response.meta['year']
    #         item['week'] = '第' + str(response.meta['week']) + '周'
    #         url = 'https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_yqq.fcg?nobase64=1&musicid={}&-=jsonp1&g_tk=5381&loginUin=0&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0'.format(
    #             i['songinfo']['songid'])
    #         headers={
    #             'Origin': 'https://y.qq.com',
    #             #'Referer': 'https://y.qq.com/m/client/v5detail/global_gift_rank.html?_bid=362',
    #             'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    #         }
    #         yield scrapy.Request(url, callback=self.parse_song_info, meta={'item': item},headers=headers)
    #



############数字专辑############
    def start_requests(self):
        for year in (2019,2019+1):
            for i in range(13):
                if i<10:
                    week='{}0{}'.format(str(year),str(i))
                else:
                    week ='{}{}'.format(str(year), str(i))
                parmas ={
                    'g_tk': '5381',
                    'uin': '0',
                    'format': 'json',
                    'inCharset': 'utf-8',
                    'outCharset': 'utf-8',
                    'notice': '0',
                    'platform': 'h5',
                    'needNewCode': '1',
                    'cmd': 'week_sale_toplist',
                    'week':week,
                    'reqtype': '2',
                    'weeklist': '1',
                    'year': '2019',
                    'week': week,
                    '_': int(time.time()*1000),
                }
                url = 'https://c.y.qq.com/v8/fcg-bin/musicmall.fcg?' + urlencode(parmas)
                yield scrapy.Request(url, meta={'week': i,'year':year},callback=self.parse_shuzi)
    def parse_shuzi(self, response):
        if json.loads(response.text)['data']['list']:
            try:
                for rank,i in enumerate(json.loads(response.text)['data']['list']):
                    item={}
                    album_mid = i['album_mid']
                    item['album_id'] =i['album_id']
                    item['albumname'] =i['album_name']
                    item['cur_rank'] = rank+1
                    item['company_name'] =i['company_name']
                    item['price']= int(i['price'])/100
                    item['last_pos'] = i['last_pos']
                    item['rising_ranks'] = str(int(item['last_pos']) - int(item['cur_rank']))
                    item['publictime']=i['publictime']
                    #item['sale_count'] = str(i['sale_info']['sale_count'])+i['sale_info']['unit']
                    item['songer'] =i['singer_name']
                    item['year'] = response.meta['year']
                    item['week']='第'+str(int(response.meta['week']))+'周'
                    try:
                        for sale_every_day in i['sale_every_day']:
                            item['sale_every_day_data'] = sale_every_day['data']
                            item['sale_every_day_salenum'] =sale_every_day['salenum']
                    except:
                        pass

                    url='https://c.y.qq.com/v8/fcg-bin/musicmall.fcg?g_tk=5381&uin=0&format=json&inCharset=utf-8&outCharset=utf-8&notice=0&platform=h5&needNewCode=1&ct=23&cv=0&albumid={0}&albummid={1}&cmd=get_base_sale_info&songlist=1&desc=1&singerinfo=1&salecount=1'.format(item['album_id'],album_mid)
                    yield scrapy.Request(url,callback=self.parse_sale_info,meta={'item':item},dont_filter=True)
            except Exception as e:
                print(e)

    def parse_sale_info(self, response):
        data = json.loads(response.text)['data']
        item = response.meta['item']
        item['album_sale_money'] =data['sale_info']['sale_money']
        item['album_price'] = int(data['price'])/100
        item['album_sale_count'] = ['sold_album_cnt']
        item['album_sale_total_money'] = data['sale_info']['sale_money']
        item['album_sale_money'] = data['sale_info']['album_count']
        item['sold_total__song_count'] = data['sale_info']['total_song_count']
        yield item
#################
########热歌榜，影视金曲榜##########
    # def start_requests(self):
    #     for year in range(2018,2019):
    #         for i in range(53):
    #             if i<10:
    #                 week = '0{}'.format(i)
    #             else:
    #                 week =i
    #
    #             parmas = {
    #                 'tpl': '3',
    #                 'page': 'detail',
    #                 'date': '{}_{}'.format(year,week),
    #                 'topid': '29',#29 影视金曲榜,26 热歌榜,
    #                 'type': 'top',
    #                 'song_begin': '0',
    #                 'song_num': '300',
    #                 'g_tk': '5381',
    #                 'loginUin': '0',
    #                 'hostUin': '0',
    #                 'format': 'json',
    #                 'inCharset': 'utf8',
    #                 'outCharset': 'utf-8',
    #                 'notice': '0',
    #                 'platform': 'yqq.json',
    #                 'needNewCode': '0',
    #             }
    #             url = self.start_urls+urlencode(parmas)
    #             yield scrapy.Request(url,meta={'week':i,'year':year},callback=self.parse_rege_yingshi)

    def parse_rege_yingshi(self, response):
        try:
            for i in json.loads(response.text)['songlist']:

                item={}
                #item['Franking_value'] = i['Franking_value']
                item['albumname'] =i['data']['albumname']
                item['songname'] =i['data']['songname']
                item['albumdesc'] =i['data']['albumdesc']
                item['albumid']=i['data']['albumid']
                interval=i['data']['interval']
                item['interval'] =str(int(int(interval/60)))+'分'+str(int(int(interval%60)))
                songid = i['data']['songid']
                item['cur_count'] = i['cur_count']
                item['old_count']=i['old_count'] #0表示新上榜
                if int(item['old_count'])==0:
                    item['rising_ranks'] = item['cur_count']
                    item['isNewComer'] = '是'
                else:
                    item['rising_ranks'] = str(int(item['old_count'])-int(item['cur_count']))
                    item['isNewComer'] = '否'
                sale_money =i['data']['pay']['paytrackprice']
                item['sale_money'] = float(sale_money)/100
                item['songer'] =[name['name'] for name in i['data']['singer']][0]
                item['year'] = response.meta['year']
                item['week']='第'+str(response.meta['week'])+'周'
                url='https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_yqq.fcg?nobase64=1&musicid={}&-=jsonp1&g_tk=5381&loginUin=0&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0'.format(i['data']['songid'])

                yield scrapy.Request(url,callback=self.parse_song_info,meta={'item':item,'songid':songid},dont_filter=True)

        except Exception as e:
            print(e)


    def parse_song_info(self,response):

        item=response.meta['item']
        try:
            item['zuoqu'] = re.search('曲：(.*?)&#',response.text).group(1)
        except:
            item['zuoqu'] =''
        try:
            item['zuoci'] = re.search('词：(.*?)&#',response.text).group(1)
        except:
            item['zuoci'] =''
        try:
            item['producer'] = re.search('制作人：(.*?)&#',response.text).group(1)
        except:
            item['producer'] =''
        try:
            item['pub_company'] = re.search('([\u4e00-\u9fa5]+发行：.*?)&#',response.text).group(1)
        except:
            item['pub_company'] = ''

        #topId = songId   cid='205360772'
        comment_count_url ='https://c.y.qq.com/base/fcgi-bin/fcg_global_comment_h5.fcg?g_tk=5381&loginUin=0&hostUin=0&format=json&inCharset=utf8&outCharset=GB2312&notice=0&platform=yqq.json&needNewCode=0&cid=205360772&reqtype=1&biztype=1&topid={}&cmd=4&needmusiccrit=0&pagenum=0&pagesize=0&lasthotcommentid=&domain=qq.com'.format(response.meta['songid'])
        yield scrapy.Request(comment_count_url,callback=self.parse_comment_count,meta={'item':item},dont_filter=True)


    def parse_comment_count(self, response):
        item = response.meta['item']
        item['commenttotal'] = json.loads(response.text)['commenttotal']
        yield item
