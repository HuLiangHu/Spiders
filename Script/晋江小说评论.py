import csv

import requests
import re
import json
def get_proxy():
    return 'http://'+requests.get("http://127.0.0.1:8080/get/").text

proxies ={ "http": "{}".format(get_proxy()), "https": "{}".format(get_proxy())}

def save_csv(filename, data):
    with open(filename, 'a', newline='', errors='ignore', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(data.values())
from scrapy import Selector
headers={
    'Cookie':'__cfduid=d247ac05efd190c2b4af8dc0af73f07921547607603; __gads=ID=85df484d6540c9f9:T=1549001280:S=ALNI_Ma2SFrhGGM4ehdV2NzcjBsCbbkv5g; UM_distinctid=168a7aa0c2c52d-0c4ed0e8a771ab-5d1f3b1c-1fa400-168a7aa0c2df69; testcookie=yes; Hm_lvt_bc3b748c21fe5cf393d26c12b2c38d99=1551924707; JJEVER=%7B%22background%22%3A%22%22%2C%22font_size%22%3A%22%22%2C%22isKindle%22%3A%22%22%7D; JJSESS=%7B%22clicktype%22%3A%22%22%2C%22referer%22%3A%22/book2/2696632%22%7D; Hm_lvt_f73ac53cbcf4010dac5296a3d8ecf7cb=1552012986; fenzhan=yc; CNZZDATA30079898=cnzz_eid%3D354853885-1552007813-%26ntime%3D1552013213; Hm_lpvt_bc3b748c21fe5cf393d26c12b2c38d99=1552013908; Hm_lpvt_f73ac53cbcf4010dac5296a3d8ecf7cb=1552014202',
    'Host':'wap.jjwxc.net',
    'Referer':'https://wap.jjwxc.net/review/2696632/13/1/690',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
}
def get_comment(episode,page,proxies):

        print('第{}章'.format(episode)+'===========第{}页========'.format(page))
        url='https://wap.jjwxc.net/review/2696632/{0}/1/{1}'.format(episode,str(page*10))
        print(proxies)
        res = requests.get(url,headers=headers,proxies=proxies)
        res.encoding = "gb2312"  # 手动指定字符编码为utf-8
        #print(res.text)
        selector = Selector(res)
        for i in selector.xpath('//ul/li'):
            item={}
            item['content'] = str(i.xpath('./a/text()').extract_first()).strip().split(' ')[0]
            print(item)
            save_csv('jj.csv',item)
if __name__ == '__main__':
    for episode in range(2, 3):
        for page in range(0, 4):
            get_comment(episode,page,proxies)