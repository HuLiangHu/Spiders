# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import re
import json
from doubancomment.items import DoubancommentItem
from ..simulation_login import simulogin
import time
import random

#登陆
username = '935718574@qq.com'
password = 'wap662838'

cookies=simulogin.login(username,password)
#print(cookies)
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
# def cookiemain():
#     #cookie = 'bid=uj5xnaIIT6I; ll="108296"; _vwo_uuid_v2=DEDE0D48A6162E8DEB9F56C545626BF17|fd9c545283c79cbebf531b4d0710d528; push_doumail_num=0; douban-fav-remind=1; __utmc=30149280; __utmc=223695111; ap=1; ue="3076815358@qq.com"; ct=y; douban-profile-remind=1; ps=y; push_noty_num=0; __utmv=30149280.14339; _ga=GA1.2.1373095289.1534302498; ap_v=1,6.0; dbcl2="143390422:SXkbwKox2f4"; ck=F-Ym; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1535104304%2C%22https%3A%2F%2Faccounts.douban.com%2Flogin%3Falias%3D3076815358%2540qq.com%26redir%3Dhttps%253A%252F%252Fmovie.douban.com%252Fsubject%252F26761328%252Fcomments%253Fstart%253D480%2526limit%253D20%2526sort%253Dnew_score%2526status%253DP%26source%3Dmovie%26error%3D1011%22%5D; _pk_id.100001.4cf6=4a2f713104e24ae7.1534300166.22.1535104304.1535102289.; _pk_ses.100001.4cf6=*; __utma=30149280.1373095289.1534302498.1535101595.1535104304.26; __utmb=30149280.0.10.1535104304; __utmz=30149280.1535104304.26.11.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/login; __utma=223695111.1621664076.1534302498.1535101595.1535104305.22; __utmb=223695111.0.10.1535104305; __utmz=223695111.1535104305.22.8.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/login'
#     trans = transCookie(cookies)
#     return trans.stringToDict()
# cookies=cookiemain()

class DoubanSpider(scrapy.Spider):
    #cookie = 'bid=SGdXSJAgZTI; ps=y; ue="3076815358@qq.com"; dbcl2="143390422:3aRU0Y2SJcA"; ck=AA5U; ap_v=1,6.0; push_noty_num=0; push_doumail_num=0; __utma=30149280.720677614.1535102876.1535102876.1535102876.1; __utmc=30149280; __utmz=30149280.1535102876.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmt=1; __utmv=30149280.14339; __utmb=30149280.2.10.1535102876; RT=r=https%3A%2F%2Fwww.douban.com%2F&ul=1535102876258&hd=1535102876511; _pk_ses.100001.4cf6=*; __utma=223695111.1546374003.1535102877.1535102877.1535102877.1; __utmb=223695111.0.10.1535102877; __utmc=223695111; __utmz=223695111.1535102877.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _pk_id.100001.4cf6=c78499ff93673a92.1535102877.1.1535103136.1535102877.'
    name = 'book'
   # allowed_domains = ['movie.douban.com']
    #start_urls = ['http://movie.douban.com/subject/26752088/comments']

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        #'Cookie': 'bid=uj5xnaIIT6I; ll="108296"; _vwo_uuid_v2=DEDE0D48A6162E8DEB9F56C545626BF17|fd9c545283c79cbebf531b4d0710d528; push_doumail_num=0; douban-fav-remind=1; __utmc=30149280; __utmc=223695111; ap=1; ue="3076815358@qq.com"; ct=y; douban-profile-remind=1; ps=y; push_noty_num=0; __utmv=30149280.14339; _ga=GA1.2.1373095289.1534302498; ap_v=1,6.0; dbcl2="143390422:SXkbwKox2f4"; ck=F-Ym; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1535104304%2C%22https%3A%2F%2Faccounts.douban.com%2Flogin%3Falias%3D3076815358%2540qq.com%26redir%3Dhttps%253A%252F%252Fmovie.douban.com%252Fsubject%252F26761328%252Fcomments%253Fstart%253D480%2526limit%253D20%2526sort%253Dnew_score%2526status%253DP%26source%3Dmovie%26error%3D1011%22%5D; _pk_id.100001.4cf6=4a2f713104e24ae7.1534300166.22.1535104304.1535102289.; _pk_ses.100001.4cf6=*; __utma=30149280.1373095289.1534302498.1535101595.1535104304.26; __utmb=30149280.0.10.1535104304; __utmz=30149280.1535104304.26.11.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/login; __utma=223695111.1621664076.1534302498.1535101595.1535104305.22; __utmb=223695111.0.10.1535104305; __utmz=223695111.1535104305.22.8.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/login',
        'Host': 'book.douban.com',
        #'Referer': 'https://movie.douban.com/subject/26761328/comments?start={}&limit=20&sort=time&status=P'.format(str(page*20)),
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        }

#测试代码
    def start_requests(self):
            start_urls =['https://book.douban.com/subject/11528339/comments/']
            #for start_url in start_urls:
            movieid = '11528339'
            start_urls = [
                'https://book.douban.com/subject/{0}/comments/hot'.format(
                    str(movieid)),
                #看过热门
                'https://book.douban.com/subject/{0}/comments/new'.format(
                    str(movieid)),  # 看过最新
                # 'https://movie.douban.com/subject/{0}/comments?start={1}&limit=20&sort=new_score&status=F'.format(
                #     str(movieid), str(page * 20)),
                # # 想看热门
                # 'https://movie.douban.com/subject/{0}/comments?start={1}&limit=20&sort=time&status=F'.format(
                #     str(movieid), str(page * 20))  # 想看最新
            ]
            for url in start_urls:
                yield scrapy.Request(url=url, meta={'movieId': movieid}, callback=self.parse_detail,
                                                      dont_filter=True,headers=self.headers,cookies=cookies)

#所有热门
    # def start_requests(self):
    #     """
    #     热门电视列表
    #     :return:
    #     """
    #     for i in range(20):
    #         url = 'https://movie.douban.com/j/search_subjects?type=tv&tag=%E7%83%AD%E9%97%A8&sort=recommend&page_limit=20&page_start={}'.format(
    #             str(i * 20))
    #         yield scrapy.Request(url)

    def parse(self, response):
        """

        :param response: 电视评论
        :return:
        """
        items = json.loads(response.text)
        for item in items['subjects']:
            name = item['title']
            #base_url = item['url'] + 'comments?start={}&limit=20&sort=new_score&status=P'
            movieid =item['id']


            # start_urls = [
            #     'https://movie.douban.com/subject/{0}/comments?start=0&limit=20&sort=new_score&status=P'.format(
            #         str(movieid)),
            #     # 看过热门
            #     'https://movie.douban.com/subject/{0}/comments?start=0&limit=20&sort=time&status=P'.format(
            #         str(movieid)),  # 看过最新
            #     # 'https://movie.douban.com/subject/{0}/comments?start={1}&limit=20&sort=new_score&status=F'.format(
            #     #     str(movieid), str(page * 20)),
            #     # # 想看热门
            #     # 'https://movie.douban.com/subject/{0}/comments?start={1}&limit=20&sort=time&status=F'.format(
            #     #     str(movieid), str(page * 20))  # 想看最新
            # ]
            start_urls=['https://book.douban.com/subject/11528339/comments/new',
                        'https://book.douban.com/subject/11528339/comments/hot']
            for url in start_urls:
                #time.sleep(random.randint(1,3))
                yield scrapy.Request(url=url, meta={'name': name, 'movieId': movieid}, callback=self.parse_detail,
                                     dont_filter=True)
                # yield scrapy.Request(url=url, meta={'name': name, 'movieId': movieid}, callback=self.parse_detail,
                #                      cookies=cookies,dont_filter=True,cookies=cookies)

    def parse_detail(self, response):
        #print('='*20,response.text)
        contents = response.xpath('//li[@class="comment-item"]')

        for content in contents:
            item = {}

            item['title'] =response.xpath('.//div[@class="aside"]//p[2]/a/text()').extract_first()
            item['comment'] = content.xpath('.//p/span[@class="short"]/text()').extract_first()
            item['author'] = content.xpath('.//h3/span[@class="comment-info"]/a/text()').extract_first()
            item['comment_time'] = content.xpath('.//h3/span[@class="comment-info"]/span[2]/text()').extract_first()
            #item['comment_time']= re.sub('\n', '', comment_time).strip()

            item['authorId']=content.xpath('.//h3/span[@class="comment-info"]/a/@href').re('https://www.douban.com/people/(.*)/')[0]
            item['commentId'] = content.xpath('@data-cid').extract_first()
            #item['bookid']=response.meta['movieId']
            item['ctime'] = str(datetime.now())
            item['votes'] = content.xpath('h3/span[@class="comment-vote"]/span/text()').extract_first()
            try:
                temp_grade = content.xpath('h3//span[starts-with(@class,"user-stars")]').re(
                    '<span class="user-stars allstar(.*?) rating".*?</span>', re.S)[0]
                item['grade'] = int(temp_grade) / 10
            except:
                item['grade']=0

            #print(item)
            yield item
        next_url = response.xpath('//li[@class="p"]/a[contains(text(),"后一页")]/@href').extract_first()
        if next_url:
            yield scrapy.Request('https://book.douban.com/subject/{}/comments/'.format(response.meta['movieId']) + next_url,
                                 callback=self.parse_detail,meta={'movieId': response.meta['movieId']}, dont_filter=True)


