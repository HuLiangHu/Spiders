import time

import requests
import re

from scrapy import Selector

with open('weibo.txt','r',encoding='utf-8') as f:
    keywords = f.readlines()

def get_weibo_url(name):
    headers={
        'Cookie':'SINAGLOBAL=1458811636830.1707.1549077723302; _s_tentry=weibo.com; Apache=4944914054394.167.1552459119481; ULV=1552459120374:9:7:7:4944914054394.167.1552459119481:1552443681429; login_sid_t=c5bc05b7cc42ccfa99707ee187963bbb; cross_origin_proto=SSL; SSOLoginState=1554178513; ALF=1586485763; SCF=AoFkAItovh-b75Fjf0ydy0jxLNCJyjTJIo51czmo_9LkwZ1aN75tMXGJ8wiE-9eGiPtHygAicw53GIb0VydsE0o.; SUHB=0sqxE5BCWLuN8M; webim_unReadCount=%7B%22time%22%3A1554949903709%2C%22dm_pub_total%22%3A2%2C%22chat_group_pc%22%3A0%2C%22allcountNum%22%3A0%2C%22msgbox%22%3A2%7D; SUBP=0033WrSXqPxfM72wWs9jqgMF55529P9D9WW889d9IOyFr2X9x2dfgFS.5JpX5KMhUgL.Fo-ESoBEShqE1hM2dJLoIfQLxKqLBonLBKeLxKqLBo-LB-2LxKnL12-LB-zLxK-L1K5L12BLxK-L1h-LBoeLxKqLBoeLBKnLxKnL12-LB-zLxK-L1K5L12BLxKML1hzLBo.LxKnLBo-L1--t; SUB=_2AkMr8k1edcPxrAZTnvwXyG3gZIpH-jyYJySoAn7uJhIyOhh77nslqSVutBF-XBDNxNx_uS8WAERYo8L6ojO-pkSA; UOR=,,www.baidu.com; WBStorage=201904111752|undefined',
        'Host': 's.weibo.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
    }
    url = 'https://s.weibo.com/weibo?q={}&wvr=6&b=1&sudaref=weibo.com&Refer=SWeibo_box'.format(name)
    res = requests.get(url,headers=headers)
   # print(res.text)
    sele = Selector(res)
    try:
        weibo_url = 'https:'+sele.xpath('//div[starts-with(@class,"card-wrap ")]//a/@href').extract_first()
        print(name,weibo_url)
        with open('weibourl.txt','a+',encoding='utf-8') as f:
            f.write(weibo_url)
            f.write('\n')
    except:
        print(name,'没有微博')
        with open('没有微博.txt','a+',encoding='utf-8') as f:
            f.write(name)
            f.write('\n')

if __name__ == '__main__':
    for keyword in keywords:
        time.sleep(10)
        get_weibo_url(keyword.strip())