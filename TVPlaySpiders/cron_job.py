#!/usr/bin/python
#-*-coding:utf-8-*-

from webplay.settings import *
import redis
from random import choice 
import sys

#set default args as -h , if no args:
if len(sys.argv) == 1: sys.argv[1:] = ["-all"]

#server = redis.from_url(REDIS_URL)

server = redis.Redis(host=REDIS_HOST, port=REDIS_PORT,password=REDIS_PASSWORD)
    
def push_urls(urls,key):
    for url in urls:
        server.lpush(key,url)
        
##############hunan tv########################
def init_hunantv():
    hunantv_urls =  ['http://m.api.hunantv.com/list?typeId=2&pageCount=1&pageSize=50&order=0&types=&area=&isvip=&style=&age=&tag=']
    push_urls(hunantv_urls,'tv_hunantv:start_urls')

##############IQiyi########################
def init_iqiyi():
    categories = ['言情剧','历史剧','武侠剧','古装剧','年代剧','农村剧','偶像剧','悬疑剧','科幻剧','喜剧','青春剧','喜剧','宫廷剧','商战剧','神话剧','穿越剧','罪案剧','谍战剧','青春剧','家庭剧','网络剧','军旅剧']    
    iqiyi_urls = ['http://search.video.qiyi.com/o?pageNum=1&mode=11&ctgName=电视剧&threeCategory=&pageSize=50&type=list&if=html5&pos=1&site=iqiyi&access_play_control_platform=15']
    #http://search.video.qiyi.com/o?pageNum=1&mode=11&ctgName=电视剧&threeCategory=&pageSize=50&type=list&if=html5&pos=1&site=iqiyi&access_play_control_platform=15
    for category in categories:
        iqiyi_urls.append('http://search.video.qiyi.com/o?pageNum=1&mode=11&ctgName=电视剧&threeCategory=%s&pageSize=50&type=list&if=html5&pos=1&site=iqiyi&access_play_control_platform=15'%category)
    push_urls(iqiyi_urls,'tv_iqiyi:start_urls')    
#############Letv#########################
def init_letv():
    letv_urls = ['http://list.le.com/apin/chandata.json?c=2&d=1&md=&o=9&p=1&s=1']
    push_urls(letv_urls,'tv_letv:start_urls')    
#############Sohu#########################
def init_sohu():
    sohu_urls = ['http://api.tv.sohu.com/v4/search/channel/sub.json?subId=187&page_size=50&offset=0&api_key=f351515304020cad28c92f70f002261c&plat=17&sver=1.0&partner=1','http://tv.sohu.com/frag/vrs_inc/phb_tv_day_100.js']
    push_urls(sohu_urls,'tv_sohu:start_urls')    
#############youku#########################
def init_youku():
    CLIENT_IDS = ['601a5d6a43a8b0f4','d68017cf81224349','70ecad56b9804e77']
    youku_urls = []
    genres = ['言情','时装','都市','剧情','家庭','古装','搞笑','偶像','警匪','历史','军事','武侠','科幻','农村','神话','儿童','优酷出品']
    for genre in genres:
        youku_urls.append('https://openapi.youku.com/v2/shows/by_category.json?client_id=%s&category=电视剧&count=20&page=1&genre=%s'%(choice(CLIENT_IDS),genre))
    push_urls(youku_urls,'tv_youku:start_urls')    
#############tudou#########################
#http://www.tudou.com/s3portal/service/pianku/data.action?pageSize=20&app=mainsitemobile&deviceType=1&tags=&tagType=3&firstTagId=3&areaCode=330300&initials=&hotSingerId=&pageNo=3&sortDesc=quality
def init_tudou():
    tudou_urls = ['http://www.tudou.com/s3portal/service/pianku/data.action?pageSize=90&app=mainsitemobile&deviceType=1&tags=&tagType=3&firstTagId=3&areaCode=310000&initials=&hotSingerId=&pageNo=1&sortDesc=quality']
    push_urls(tudou_urls,'tv_tudou:start_urls')    

#############qq#########################
def init_qq():
#'http://film.qq.com/paylist/0/pay_-1_-1_-1_-1_0_0_0_40_-1_1.html','http://mobile.video.qq.com/fcgi-bin/dout_pc?auto_id=851&itype=-1&iarea=-1&iyear=-1&itrailer=0&iedition=-1&sort=2&page=0&pagesize=20&otype=json'
    qq_urls = ['http://mobile.video.qq.com/fcgi-bin/dout_pc?auto_id=851&itype=-1&iarea=-1&iyear=-1&itrailer=0&iedition=-1&sort=2&page=0&pagesize=20&otype=json',
    'http://film.qq.com/paylist/0/pay_-1_-1_-1_-1_0_0_0_40_-1_1.html','http://v.qq.com/rank/detail/2_-1_-1_-1_2_-1.html']
    push_urls(qq_urls,'tv_qq:start_urls')
    
#############qq#########################
def init_kankan():
    kankan_urls = ['http://list.pad.kankan.com/common_mobile_list/act,1/type,teleplay/os,az/osver,5.1/productver,5.0.0.16/genre,_ALL_/sort,hits/genre,_ALL_/year,_ALL_/area,_ALL_/status,_ALL_/page,1/pernum,200/']
    push_urls(kankan_urls,'tv_kankan:start_urls')
    
#############qq#########################
def init_pptv():
    pptv_urls = ['http://m.pptv.com/sort_list/2------6---1.html']
    push_urls(pptv_urls,'tv_pptv:start_urls')
    
    

def init_all():
    init_iqiyi()
    init_qq()
    init_letv()
    init_sohu()
    init_youku()
    init_tudou()
    init_hunantv()
    init_pptv()
    init_kankan()

if __name__ == "__main__":
    mode = sys.argv[1].upper()
    if mode == "-ALL":
        init_all()
    if mode == "-IQIYI":
        init_iqiyi()
    if mode == "-LETV":
        init_letv()
    if mode == "-QQ":
        init_qq()
    if mode == "-HUNANTV":
        init_hunantv()
    if mode == "-SOHu":
        init_sohu()
    if mode == "-YOUKU":
        init_youku()    
    if mode == "-TUDOU":
        init_tudou()
    if mode == "-PPTV":
        init_pptv()
    if mode == "-KANKAN":
        init_kankan()
    #init_all()
    #init_hunantv()
    #init_iqiyi()
    #init_letv()