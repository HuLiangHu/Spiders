import requests
import json
import time
def save_csv(filename,data):
    import csv
    with open(filename, 'a',newline='', errors='ignore',encoding='utf-8') as f:
        writer =csv.writer(f)
        writer.writerow(data.values())
def get_proxy():
    return requests.get("http://127.0.0.1:8080/get/").text

headers={
    'Host': 'yuedu.163.com',
    #'Referer': 'http://yuedu.163.com/source/18cecd064de348329fd578428ba9b79b_4',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
}
for i in range(1,728):
    proxies = {"http://": "{}".format(get_proxy()), "https://": "{}".format(get_proxy())}
    print(i)
    time.sleep(1)
    url = 'http://yuedu.163.com/snsComment.do?operation=get&type=2&id=18cecd064de348329fd578428ba9b79b_4&page={}'.format(i)
    res = requests.get(url,headers=headers,proxies=proxies)
    for info in json.loads(res.text)['data']:
        item={}
        item['comment'] = info['text']
        item['posttime'] = info['posttime']
        item['author']  =info['username']
        item['stars'] = info['stars']
        print(item)
        save_csv('data.csv',item)