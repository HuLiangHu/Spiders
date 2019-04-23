# -*- coding: utf-8 -*-
from datetime import datetime

import scrapy
import re
from scrapy.http import Request
from traceback import format_exc
from scrapy import Selector

from douban.spiders.Utils_model.font import font_creator
from ..items import  ReYingMovie



class MaoyanNewSpider(scrapy.Spider):
    name = 'maoyannew'
    headers = {
        #'cookie': '__mta=252534326.1543976794094.1543977465815.1543978964770.7; uuid_n_v=v1; uuid=2D4AEBC0F83511E8B7BE93B67D64D2692F8805DA758046F98ACC9CD65F4929E3; _csrf=1c96cd3cf461b4e7521dabdbc9648058c576f4cb434ce90d15c8349085789b86; _lx_utm=utm_source%3Dgoogle%26utm_medium%3Dorganic; _lxsdk_cuid=1677c3035a5c8-00e8e2a8e4f39c-35617600-13c680-1677c3035a5c8; _lxsdk=2D4AEBC0F83511E8B7BE93B67D64D2692F8805DA758046F98ACC9CD65F4929E3; __mta=252534326.1543976794094.1543978964770.1544083367162.8; _lxsdk_s=167828a6457-7b0-b3c-766%7C%7C2',
        'referer': 'https://maoyan.com/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
    }

    #allowed_domains = ['maoyan.com', 'api.xdaili.cn', 'xdaili-api']

    start_urls = ['https://maoyan.com/films?showType=1',#正在热映
                  'https://maoyan.com/films?showType=2']#即将上映

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.pare_movielist,dont_filter=True,headers=self.headers)

    def pare_movielist(self,response):
        movie_links = response.xpath('//div[@class="movie-item"]/a/@href').extract()
        for link in movie_links:
            url='https://maoyan.com'+link
            #print(url)
            yield scrapy.Request(url,callback=self.parse_detail)
        next_url = response.xpath("//li/a[text()='下一页']/@href").extract_first()
        #print(next_url)
        if next_url:
            next_url = 'https://maoyan.com/films' + str(next_url)
            #print("下一页的链接:", next_url)
            self.headers['referer'] = response.url
            yield Request(next_url,callback=self.pare_movielist,dont_filter=True,headers=self.headers)

    def parse_detail(self, response):

        html_font = font_creator(response.text)
        resp = Selector(text=html_font)
        item = ReYingMovie()


        item['name'] = response.xpath('//div[@class="movie-brief-container"]/h3/text()').extract_first()
        item["createdtime"] = str(datetime.now())
        item["movieDate"] = response.xpath('//li[@class="ellipsis"][3]/text()').extract_first()[:-4]
        item["comefrom"] = "猫眼"
        item["filmid"] = re.findall(r'\d+', response.url)[0]
        item["crawldate"] = str(datetime.today())
        item["createdtime"] = str(datetime.now())
        try:
            item['Grade'] = resp.xpath('//p[contains(text(),"用户评分")]/..//span[@class="index-left info-num "]/span/text()').extract_first()
            # print(Grade)
        except:
            item['Grade'] =None

        item['want']=resp.xpath('//p[text()="想看数"]/..//span[@class="stonefont"]/text()').extract_first()

        try:
            piaofang = resp.xpath(
                '//p[contains(text(),"票房")]/..//span[@class="stonefont"]/text()').extract_first() + response.xpath(
                '//span[@class="unit"]/text()').extract_first()

            item['piaofang'] = self.str2float(piaofang)
        except:
            item['piaofang'] = None
        try:
            gradePeople = resp.xpath('//span[contains(text(),"人评分")]/..//span[@class="stonefont"]/text()').extract_first()
            item['gradePeople'] = self.str2float(gradePeople)
        except:
            item['gradePeople'] =None
        yield item



    def str2float(self,data):
        if '万' in data:
            data = int(float(re.search('(\d+)', data).group(1)) * 10000)
        elif '亿' in data:
            data = int(float(re.search('(\d+)', data).group(1)) * 100000000)
        else:
            data = data
        return data
    def error_back(self, e):
        """
        报错机制
        """
        self.logger.error(format_exc())
