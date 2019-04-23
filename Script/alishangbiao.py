import re
import time
from urllib.parse import urlencode

import requests
import json
import csv


def save_csv(filename, data):
    with open(filename, 'a', newline='', errors='ignore', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(data.values())


baseurl= 'https://tm-api.aliyun.com/trademarksearch/list.jsonp?'
def get_uid(page):
    params ={
        'classification':'',
        'product':'',
        'keyword':'上海克顿文化传媒有限公司',
        'searchType':'3',
        'status':'0',
        'pageNum':page,
        'pageSize':'20',
        'umidToken':'1552374129542:0.6511318947140077',
        'nvc':'{"a":"N2RG","c":"1552374129542:0.6511318947140077","d":"nvc_register","j":{"test":1},"b":"115#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","e":"tI5CnbGcIPZvgDEEvz2Rpyr5fo8aymMDkeBHmRLPIraOu02fmTbbQ8TJwo5S8wQydpZlaNoVDOI0RqekmpQtSNFMCtVLDFKzAEBhPYcSUnVaEHOEr6ZMz1BWZHaiuscrgXuwer0toy_sPQhGzpHhjKinpMZEFZKEfd-zOAMDiUCxNhHyyzjqjekUPz83kk7nuj_r0ZDUxx5o14nClKpcnA","f":null,"g":null}',
    }

    url = baseurl+urlencode(params)
    response = requests.get(url,headers=headers,verify=False)
    print(response.text)
    for i in json.loads(response.text)['data']['data']:
        ownerName = re.sub('<.*?>','',i['ownerName'])
        if ownerName=='上海克顿文化传媒有限公司':
            uid = i['uid']
            get_detail_info(uid)
        #save_csv('商标.csv',item)
def get_detail_info(uid):
    url='https://tm-api.aliyun.com/trademarksearch/detail.jsonp?uid={}&umidToken=1552375563261%3A0.3513868645660396&nvc=%7B%22a%22%3A%22N2RG%22%2C%22c%22%3A%221552375563261%3A0.3513868645660396%22%2C%22d%22%3A%22nvc_register%22%2C%22j%22%3A%7B%22test%22%3A1%7D%2C%22b%22%3A%22115%231KrPTf1O1Twtmt3OG5f21Csod6cCSJnN63qTCNXZW1Ke4VZ1SAkTNoSrJJ%2FiQvf1pX0GyzPANIfyOt%2F8zSCWi%2FJJhUU4OkNVaLBXuzFQOSAPet%2F8sMNQiQJWhefURDdDaLKKyrPQASAPet%2F4uWiQiQWRhUU4BHNcaTBXz5%2FGmGhtD83mRWId95TsMJaMSBWWnMA%2FwZssorHxEoGx3Yn6%2Bf9meTMIpvyZAkvmwbUhQugyNs27f4kE0ufBuP6R7ofAONPsqWQp954jIk7VDJlxBcdDxkaZUHAHyfD0evQHTVJDEW40r7uLsdtTO%2F8W7lIMET2lBvZV8NAqo6B32YnawwIu56x0RM%2BYQTKPzSfhBrP4Dz1m2H%2BihbaYoSCZZXm4VbvEYokwMemLzKilQ3CwPQj%2FGXncLiSXfc1zYWqsomc6UG%2B7XnQlhv7usDtN0I3OX3HQNcizxWsGmzGbcSgFmC4DRakFp%2FrJKiJO8kngU1FAi3%2BAvrqo30P4bf%3D%3D%22%2C%22e%22%3A%22tI5CnbGcIPZvgDEEvz2Rpyr5fo8aymMDkeBHmRLPIraOu02fmTbbQ8TJwo5S8wQydpZlaNoVDOI0RqekmpQtSNFMCtVLDFKzAEBhPYcSUnVaEHOEr6ZMz1BWZHaiuscrgXuwer0toy_sPQhGzpHhjKinpMZEFZKEfd-zOAMDiUCxNhHyyzjqjekUPz83kk7nuj_r0ZDUxx5o14nClKpcnA%22%2C%22f%22%3Anull%2C%22g%22%3Anull%7D'.format(uid)
    response = requests.get(url, headers=headers, verify=False)
    print(response.text)
    i = json.loads(response.text)['data']

    item={}
    item['商标名称'] = i['name']
    item['代理人名称'] = i['agency']
    item['申请日期']=i['applyDate']
    item['专用权期限']=i['exclusiveDateLimit']
    item['类似群']=i['bizProduct']
    item['类别']=i['classification']
    item['当前状态']=i['lastProcedureStatus']
    item['申请人地址']=i['ownerAddress']
    item['类似群']=i['product']
    item['注册号']=i['registrationNumber']
    item['初审公告日期']=i['preAnnDate']
    item['注册公告日期']=i['regAnnDate']
    item['注册公告期号']=i['regAnnNum']
    item['商标流程'] = ','.join(info['procedureDate'] +'-'+ info['procedureStep'] for info in i['procedures'])
    item['商标公告'] =','.join(info['annDate'] +'-'+ info['annTypeName']+' '+'第'+info['annNum']+'期' for info in i['announces'])
    item['图片']=i['image']
    print(item)
    save_csv('商标.csv',item)


if __name__ == '__main__':
    headers = {
        'Referer': 'https://tm.aliyun.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
    }
get_detail_info('5a079845d1ad4a27852ff8e32ad578af')