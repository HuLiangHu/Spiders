# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import os
from datetime import datetime as dt
import re
import datetime
import pymysql
import scrapy
import ssl
import json
from urllib.parse import urlencode
from UweelSpider.items import UweelSpiderItem
from scrapy.utils.project import get_project_settings
from urllib3 import encode_multipart_formdata
from .WeiboCookie import copy_cookie
import requests
import random
ssl._create_default_https_context = ssl._create_unverified_context

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
def cookiemain():
    trans = transCookie(copy_cookie)
    return trans.stringToDict()

def del_expired_files():
    dirToBeEmptied = [r'.\Uweel_Spider\Videos',r'.\Uweel_Spider\Images']  # 需要清空的文件夹
    ds = list(os.walk(random.choice(dirToBeEmptied)))  # 获得所有文件夹的信息列表
    delta = datetime.timedelta(days=5)  # 设定5天前的文件为过期
    now = datetime.datetime.now()  # 获取当前时间
    for d in ds:  # 遍历该列表
        os.chdir(d[0])  # 进入本级路径，防止找不到文件而报错
        if d[2] != []:  # 如果该路径下有文件
            for x in d[2]:  # 遍历这些文件
                ctime = datetime.datetime.fromtimestamp(os.path.getctime(x))  # 获取文件创建时间
                if ctime < (now - delta):  # 若创建于delta天前
                    os.remove(x)  # 则删掉

class UweelWeiboSpider(scrapy.Spider):
    name = 'uweel_weibo'
    #allowed_domains = ['weibo.com']
    baseurl = 'https://weibo.com/p/aj/v6/mblog/mbloglist?'
    api ='https://m.weibo.cn/api/container/getIndex?'
    containId ='https://m.weibo.cn/api/container/getIndex?type=uid&value={}'
    headers = {
        'Cookie':copy_cookie,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }
    with open('token.txt', 'r') as f:
        token = f.read()
    del_expired_files() #删除过期文件

    settings = get_project_settings()
    FILE_UPLOAD_AIP = settings['FILE_UPLOAD']
    conn = pymysql.connect(
        user=settings['MYSQL_USER'],
        passwd=settings['MYSQL_PASSWD'],
        db=settings['MYSQL_DBNAME'],
        host=settings['MYSQL_HOST'],
        charset="utf8",
        use_unicode=True
    )
    cursor = conn.cursor()

    def start_requests(self):

        self.cursor.execute("SELECT * FROM `uweel_keywords`")
        datas = self.cursor.fetchall()
        for data in datas:
            circleId = data[1]
            circleName = data[2]
            url = data[3]

            if 'https' in url:
                url = url
            else:
                url = url.replace('http','https')
            yield scrapy.Request(url,callback=self.parse_uid,cookies=cookiemain(),dont_filter=True,meta={'circleName':circleName,
                                                                                                         'circleId':circleId,
                                                                                                        })

    def parse_uid(self, response):

        uid = re.search('CONFIG\[\'oid\'\]=\'(.*)\'',response.text).group(1)
            #id ='1259110474'
        if len(str(uid))>4:
            url = self.containId.format(uid)
            yield scrapy.Request(url,meta={'id':uid,
                                           'circleId':response.meta['circleId'],
                                           'circleName':response.meta['circleName'],
                                           },callback=self.parse_containerId,cookies=cookiemain())


    def parse_containerId(self, response):
       # print(response.text)
        content = json.loads(response.text)['data']
        for data in content['tabsInfo']['tabs']:
            if (data.get('tab_type') == 'weibo'):
                containerid = data.get('containerid')

        parmas ={
            'uid': response.meta['id'],
            'luicode': '10000011',
            'type': 'uid',
            'value': response.meta['id'],
            'containerid': containerid,
            'page': '1'
        }
        url = self.api+urlencode(parmas)
        yield scrapy.Request(url, callback=self.parse_item,meta={'parmas':parmas,
                                                                 'circleId': response.meta['circleId'],
                                                                 'circleName': response.meta['circleName'],
                                                                 }, headers=self.headers, dont_filter=True,cookies=cookiemain())

    def parse_item(self, response):
        total_count= json.loads(response.text)['data']['cardlistInfo']['total']
        total_page = int(total_count)//10
        if json.loads(response.text)['data']['cards']:
            for info in json.loads(response.text)['data']['cards']:
                item =UweelSpiderItem()
                if info['card_type'] ==9:
                    try:
                        item['circleName'] = response.meta['circleName']

                        item['wid'] = info['mblog']['id']
                        content = info['mblog']['text']
                        type = info['mblog']['page_info']['type'] #type=='article'
                        """
                        判断文章大类
                        """
                        if type=='article':
                            item['article_type'] = "LONG_TEXT"
                            item['title'] = info['mblog']['page_info']['page_title']
                            content_url = info['mblog']['page_info']['page_url']
                            yield scrapy.Request(content_url,callback=self.parse_longtext_content,meta={'item':item}, headers=self.headers, dont_filter=True,cookies=cookiemain())
                        else:
                            item['article_type'] = "SHORT_TEXT"
                            item['content'] = str(re.sub('<.*?>', ' ', content).lstrip()).replace('#','').replace('&quot;','"')
                            if len(item['content'].split('      ')[0])>10:
                                item['title'] = item['content'].split('，')[0]
                            else:
                                item['title'] = item['content'].split('      ')[0]
                            try:
                                video_url =info['mblog']['page_info']['media_info']['stream_url_hd']
                                """
                                """
                                video_name = re.search('.*/(.*?.mp4)',video_url).group(1)
                                self.download_video(video_name,video_url)

                                new_video_address = self.get_video_address(video_name)

                                item['video_url'] = new_video_address

                                video_cover  =info['mblog']['page_info']['page_pic']['url']
                                video_cover_name = str(video_cover.split('/')[-1]).replace('.jpg','')
                                self.download_img(video_cover_name,video_cover)
                                new_video_cover_address = self.get_image_address(video_cover_name)

                                item['video_cover'] = new_video_cover_address
                                #item['video_duration']=info['mblog']['page_info']['media_info']['duration']
                            except:
                                item['video_url'] =None
                                item['video_cover'] =None
                                # item['video_duration'] =None
                            new_img_address_list=[]
                            try:
                                for i in info['mblog']['pics']:

                                    self.download_img(i['pid'], i['url'])

                                    """
                                    self.download_img(i['pic'],i['url']) #old 
                                    """
                                    new_img_address=self.replace_file(i['url'],
                                                                      i['url'],#原始的图片url
                                                      self.get_image_address(i['pid']))
                                    new_img_address_list.append(new_img_address)

                                    item['img_url']=','.join(new_img_address_list)

                            except:
                                item['img_url'] = None
                            """
                            判断文章具体类型
                            """
                            if item['img_url']:
                                item['definite_type'] = 'PICTURE'
                            elif item['video_url']:
                                item['definite_type'] = 'VIDEO'
                            else:
                                item['definite_type'] = "TEXT"
                            item['long_text_cover'] =None
                            item['long_text_summary'] =None
                            item['circleId'] = response.meta['circleId']
                            item['resource'] = 'weibo'
                            item['crawldate'] = str(dt.now()).split(' ')[0]

                    except Exception as e:

                        item['circleName'] = response.meta['circleName']
                        item['wid'] = info['mblog']['id']
                        content = info['mblog']['text']
                        item['content'] = str(re.sub('<.*?>', ' ', content).lstrip()).replace('#', '').replace('&quot;','"')
                        if len(item['content'].split('      ')[0]) > 10:
                            item['title'] = item['content'].split('，')[0]
                        else:
                            item['title'] = item['content'].split('      ')[0]
                        item['definite_type']="TEXT"
                        item['video_url'] = None
                        item['video_cover'] = None
                        item['img_url'] = None
                        item['article_type'] = "SHORT_TEXT"
                        item['long_text_cover']=None
                        item['long_text_summary']=None
                        item['resource'] ='weibo'
                        item['circleId']=response.meta['circleId']
                        item['crawldate'] = str(dt.now()).split(' ')[0]
                    finally:
                        yield item
            #print(total_page)
            if int(total_page)<99:
                pageNum = int(total_page)
            else:
                pageNum = 100
            parmas = response.meta['parmas']
            for page in range(1,2):
                parmas['page'] =page
                url = self.api+urlencode(parmas)
                yield scrapy.Request(url,callback=self.parse_item,meta={'parmas':parmas,
                                                                        'circleId': response.meta['circleId'],
                                                                        'circleName': response.meta['circleName'],
                                                                        },headers=self.headers,cookies=cookiemain())
                self.headers['Referer'] =url

    def parse_longtext_content(self, response):
        item = response.meta['item']
        content= re.search('\"content\": \"(.*)\"',response.text).group(1).replace('\\','')
        long_text_imgae_all = re.findall('src=\"(.*?)\"',content)

        """
        循环遍历content里面包含的图片，替换图片地址
        """
        img_list=[]
        content_list = []
        content_str =''
        for img in content.split('<img src='):
            img_list.append(img)

        for j,i in enumerate(long_text_imgae_all):
            img_name = i.split('/')[-1]
            content_list.append(img_list[0])
            content_list.append('<img src=')
            #下载图片
            self.download_img(img_name,i)      #old address
            # self.get_image_address(img_name)   new address
            new_content =self.replace_file(img_list[j+1],i,self.get_image_address(img_name))
            content_list.append(new_content)
        for i in content_list:
            content_str += i
        item['content'] = content_str

        try:
            item['long_text_summary'] = re.search('\"summary\": \"(.*?)\"',response.text).group(1)
        except:
            item['long_text_summary']  = None
        try:
            long_text_cover = re.search('\"cover_img\": \"(.*?)\"',response.text).group(1)
            """
            图片替换
            1.下载图片 download_img
            2.生成新的图片地址
            3.替换成新的图片地址
            """
            self.download_img(long_text_cover.split('/')[-1],long_text_cover)
            new_long_text_cover_address = self.get_image_address(str(long_text_cover.split('/')[-1]).replace('.jpg',''))
            item['long_text_cover'] = self.replace_file(long_text_cover,long_text_cover,new_long_text_cover_address)
        except:
            item['long_text_cover'] = None
        item['video_url'] =None
        item['img_url'] =None
        item['definite_type'] ="ARTICLE"
        item['video_cover'] = None
        item['crawldate'] = str(dt.now()).split(' ')[0]
        yield item

    def get_token(self):
        res = requests.get('http://svc.uweel.test.crotondata.cn/api/in/v1/user/getRobotFileAuth').text
        token = json.loads(res)['data']
        return token

    def is_expried_token(self,token):
        """
        判断token是否有效
        :param token: 从文件从读取token，检查是否有效
        :return: 如果失效，重新获取token（get_token），将新的token写入token.txt
        """
        headers = {
            'Authorization': token
        }
        res = requests.post(self.FILE_UPLOAD_AIP, headers=headers)
        if json.loads(res.text)['statusCode'] == 9999:
            new_token = self.get_token()
            with open('token.txt', 'w') as f:
                f.write(new_token)
        else:
            new_token = token
        return new_token

    def get_image_address(self,old_img_name):
        headers = {
            'Authorization': self.is_expried_token(self.token)
        }
        data = {
            'files': ('{}.jpg'.format(old_img_name), open(r'.\UweelSpider\Images\{}.jpg'.format(old_img_name), 'rb').read())
        }
        encode_data = encode_multipart_formdata(data)
        data = encode_data[0]
        headers['Content-Type'] = encode_data[1]
        res = requests.post(self.FILE_UPLOAD_AIP, headers=headers, data=data)
        for i in json.loads(res.text)['data']:
            new_img_address = i['mediaUuid']
        return 'https://cdn.uweel.com/' + new_img_address
        #return new_img_address

    def download_img(self,img_name, url):
        file_list = os.listdir(r'.\UweelSpider\Images')
        if img_name not in file_list:
            res = requests.get(url)
            if '.jpg' in img_name or '.png' in img_name:
                img_name = img_name
            else:
                img_name=img_name+'.jpg'
            with open(r'.\UweelSpider\Images\{}'.format(img_name), 'wb') as f:
                f.write(res.content)

            return img_name

    def download_video(self,video_name,video_url):
        file_list = os.listdir(r'.\UweelSpider\Videos')
        if video_name not in file_list:
            r = requests.get(video_url, stream=True)
            with open(r'.\UweelSpider\Videos\{}'.format(video_name), "wb") as mp4:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        mp4.write(chunk)

    def get_video_address(self,old_video_name):
        headers = {
            'Authorization': self.is_expried_token(self.token)
        }
        data = {
            'files': ('{}'.format(old_video_name), open(r'.\UweelSpider\Videos\{}'.format(old_video_name), 'rb').read())
        }
        encode_data = encode_multipart_formdata(data)
        data = encode_data[0]
        headers['Content-Type'] = encode_data[1]
        res = requests.post(self.FILE_UPLOAD_AIP, headers=headers, data=data)
        for i in json.loads(res.text)['data']:
            new_img_address = i['mediaUuid']
        return 'https://cdn.uweel.com/' + new_img_address
    def replace_file(self,content,old_file,new_file):
        """
        替换图片，视频
        :param file: old图片地址
        :return: new图片地址
        """
        content = re.sub(old_file, new_file, content)
        return content


