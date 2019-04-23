import requests
from scrapy import Selector
import time
import csv
def save_csv(filename, data):
    with open(filename, 'a', newline='', errors='ignore', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(data.values())

copy_cookie = 'SINAGLOBAL=1458811636830.1707.1549077723302; wb_cmtLike_5264246287=1; un=18616747293; TC-V5-G0=5fc1edb622413480f88ccd36a41ee587; _s_tentry=weibo.com; Apache=4944914054394.167.1552459119481; ULV=1552459120374:9:7:7:4944914054394.167.1552459119481:1552443681429; TC-Page-G0=841d8e04c4761f733a87c822f72195f3; SSOLoginState=1552470000; Ugrow-G0=e66b2e50a7e7f417f6cc12eec600f517; ALF=1584093230; SCF=AoFkAItovh-b75Fjf0ydy0jxLNCJyjTJIo51czmo_9LkbSdc4Az_t4nHCo13JmIzjhPCE8q4NRAFq6abhKz5Nu0.; SUHB=0TPl58JoYgc5bP; UOR=,,news.ifeng.com; SUB=_2AkMr04uEf8PxqwJRmP4UyWjlbIlwzQDEieKdj3pfJRMxHRl-yT9jqhdftRB6AFOla6vUcHJ6-gOQW22ajgwg1eId3YAB; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9W5pQeC.dHwOguRkCkZls5HX'

with open('weibo.txt','r',encoding='utf-8') as f:
    names = f.readlines()

for name in names:
    time.sleep(1)
    url ='http://huati.weibo.com/k/{}'.format(name.strip())
    headers={
        'Cookie': copy_cookie,
        'Host': 'huati.weibo.com',
        #'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
    }
    res = requests.get(url,headers=headers, allow_redirects=False)
    print(res.status_code)
    if res.status_code == 301:
        url =res.headers['Location']
        print('first',url)
        headers['Host']='weibo.com'
        #headers['Cookie']='SINAGLOBAL=1458811636830.1707.1549077723302; wb_cmtLike_5264246287=1; un=18616747293; TC-V5-G0=5fc1edb622413480f88ccd36a41ee587; _s_tentry=weibo.com; Apache=4944914054394.167.1552459119481; ULV=1552459120374:9:7:7:4944914054394.167.1552459119481:1552443681429; SSOLoginState=1552470000; Ugrow-G0=e66b2e50a7e7f417f6cc12eec600f517; login_sid_t=c5bc05b7cc42ccfa99707ee187963bbb; cross_origin_proto=SSL; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WW889d9IOyFr2X9x2dfgFS.5JpX5KMhUgL.Fo-ESoBEShqE1hM2dJLoIfQLxKqLBonLBKeLxKqLBo-LB-2LxKnL12-LB-zLxK-L1K5L12BLxK-L1h-LBoeLxKqLBoeLBKnLxKnL12-LB-zLxK-L1K5L12BLxKML1hzLBo.LxKnLBo-L1--t; ALF=1585281900; SCF=AoFkAItovh-b75Fjf0ydy0jxLNCJyjTJIo51czmo_9LkHlFPm6g9sPSdK_B3wM6HpqfnTj3_3a7aLW9h0xcMKxU.; SUB=_2A25xmDe9DeRhGeNM7VYT9CjOwzuIHXVS7C51rDV8PUNbmtAKLWrFkW9NThMvEiSnJfy_1pMs73-kmT9LWjt-Qd9F; SUHB=0vJ4TE9jfKiW2y; wb_view_log_5264246287=1920*10801; UOR=,,tech.ifeng.com; TC-Page-G0=45685168db6903150ce64a1b7437dbbb|1553764272|1553764173; webim_unReadCount=%7B%22time%22%3A1553764193563%2C%22dm_pub_total%22%3A1%2C%22chat_group_pc%22%3A0%2C%22allcountNum%22%3A0%2C%22msgbox%22%3A2%7D'
        res =  requests.get(url,headers=headers, allow_redirects=False)

        if res.status_code == 301:
            url = res.headers['Location']
            print('第二次：', url)

            headers['Host'] = 'weibo.com'
            headers['Cookie'] = copy_cookie
            resp = requests.get(url, headers=headers, allow_redirects=False)

            import re

            item = {}

            item['name'] = re.search('超有话聊。(.*?)超话，阅读', resp.text).group(1)
            item['read_count'] = re.search('阅读:(\d+),', resp.text).group(1)
            item['tiezi_count'] = re.search('帖子:(\d+),', resp.text).group(1)
            item['fans_count'] = re.search('粉丝:(\d+)', resp.text).group(1)
            print(item)
            save_csv('weibochaohua.csv',item)