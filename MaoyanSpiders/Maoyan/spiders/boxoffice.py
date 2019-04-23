# -*- coding: utf-8 -*-
import time
from scrapy.spiders import Spider
from Maoyan.items import BoxofficeItem, MaoyanItem, AudiencesItem, exclusiveieceItem, CityItem
import re
import json
import scrapy
import sys
from datetime import date, datetime, timedelta
from Maoyan.fonthelper import *
from scrapy.selector import Selector


class BoxofficeSpider(Spider):
    name = "boxoffice"
    yesterday = date.today() - timedelta(days=1)
    start_urls = ['http://piaofang.maoyan.com/?date=' + yesterday.strftime('%Y-%m-%d')]
    fontMapping = []

    def parse(self, response):
        if re.search('date=([\d-]+)', response.url):
            date = re.search('date=([\d-]+)', response.url).group(1)
        else:
            yesterday = date.today() -  timedelta(days=1)
            date = yesterday.strftime('%Y-%m-%d')

        for item in response.xpath('//div[@id="ticket_tbody"]/ul/@data-com').extract():
            #hrefTo,href:'/movie/338424?_v_=yes
            movieid = re.search('\/movie\/(\d+)',item).group(1)
            request = scrapy.Request('http://piaofang.maoyan.com/movie/%s'% movieid, callback=self.parse_item,dont_filter=True) 
            request.meta['filmid'] = movieid
            yield request

            #http://piaofang.maoyan.com/movie/338349/wantindex
            request = scrapy.Request('http://piaofang.maoyan.com/movie/%s/wantindex'% movieid, callback=self.parse_audiance,dont_filter=True) 
            request.meta['filmid'] = movieid
            yield request

            request = scrapy.Request('http://piaofang.maoyan.com/movie/%s/boxshow'% movieid, callback=self.parse_dailyboxoffice,dont_filter=True) 
            request.meta['filmid'] = movieid
            yield request

            url = 'http://piaofang.maoyan.com/movie/%s/cityBox?date=%s' %(movieid,date)
            request = scrapy.Request(url, callback=self.parse_city, dont_filter=True)
            request.meta['filmid'] = movieid
            yield request
    
    def parse_dailyboxoffice(self,response):

        #dates = response.xpath('//div[@class="t-table"]/div/div[@class="t-row"]/div[@class="t-col"]/span/b/text()').extract()

        jsonData = json.loads(re.search('var boxData = ({.+})',response.body_as_unicode()).group(1))
        filmid = re.search('movie/(\d+)/boxshow',response.url).group(1)
        dailiboxoffices= jsonData['data']
        for boxoffice in dailiboxoffices:
            item = BoxofficeItem()
            item['filmid'] = filmid
            item['day'] = boxoffice['showDate']
            item['boxOffice'] = boxoffice['boxInfo']
            item['boxOfficePercent'] = boxoffice['boxRate']
            item['exclusivePiecePercent'] = boxoffice['seatRate']
            item['personAmount'] = boxoffice['avgShowView']
            yield item

    def parse_city(self,response):
        date = re.search('date=([\d-]+)',response.url).group(1)

        jsonData = json.loads(re.search('var cityBoxData = ({.+})',response.body_as_unicode()).group(1))
        filmid =  response.meta['filmid']
        cityboxoffices= jsonData['data']

        for box in cityboxoffices:
            city = CityItem()
            city['filmid'] = filmid
            city['day'] = date
            city['city'] = box['cityName']
            city['boxOffice'] = box['dayBox']
            city['boxOfficePercent'] = box['boxRate']
            city['exclusivePiecePercent'] = box['showRate']
            city['boxOfficeAmount'] = box['totalBox']
            city['seatsPercent'] = box['seatRate']
            city['goldFieldPercent'] = box['goldShowRate']
            city['personAmount'] = box['viewerNum']
            city['person'] = box['viewerNum']
            city['filmTimes'] = box['showNum']
            yield city

    def decode_value(self,fontMapping,rawdata):
        charts = []
        for chart in rawdata:
            decimalCode = ord(chart)
            if str(decimalCode) in fontMapping: 
                charts.append(str(fontMapping[str(decimalCode)] ))
            else:
                charts.append(str(chart) )
        return ''.join(charts)
    
    def parse_audiance(self,response):
        audience = AudiencesItem()
        audience['filmid'] = response.meta['filmid']
        if(re.search('({"visible":.+})',response.body_as_unicode())):
            age = re.search('({"visible":.+})',response.body_as_unicode()).group(1)  
            ages = json.loads(age)
            if 'ageRatesChart' in  ages:
                points = ages['ageRatesChart']['series'][0]['points']
                audience['agegroup1'] = points[0]['yValue']
                audience['agegroup2'] = points[1]['yValue']
                audience['agegroup3'] = points[2]['yValue']
                audience['agegroup4'] = points[3]['yValue']
                audience['agegroup5'] = points[4]['yValue']
                audience['agegroup6'] = points[5]['yValue']
                #audience['agegroup7'] = points[6]['yValue']
        male = re.search('<div class=\"stackcolumn-bar left\" style=\"width: ([\d\.]+)%',response.body_as_unicode()).group(1) 
        female = re.search('<div class=\"stackcolumn-bar right\" style=\"width: ([\d\.]+)%',response.body_as_unicode()).group(1) 
        audience['male'] = male
        audience['female'] = female
        yield audience

    def parse_item(self, response): 
        # parse base info 
        matchs = re.search('data:application\/font-\w+;charset=utf-8;base64,(.*)\) format\("(\w+)"\);',response.body_as_unicode())
        b64font = matchs.group(1)
        fontMapping = extract_fonts(b64font)  
        item = MaoyanItem()

        item['filmid'] = response.url.split("/")[-1]
        item['url'] = response.url
        item['name'] = response.xpath('//p[@class="info-title"]/text()').extract_first()
        
        
        unicodeStr = response.xpath('//div[@class="info-score"]/a/p[@class="score-num "]/i/text()').extract_first()
        if unicodeStr:
            item['score'] = self.decode_value(fontMapping,unicodeStr) 
        else:
            item['score']  = ''

        unicodeStr = response.xpath('//p[@class="info-wish"]/span/i/text()').extract_first()
        if unicodeStr:
            item['wish'] =  self.decode_value(fontMapping,unicodeStr) 
        else:
            item['wish'] = ''

        item['category'] = ''
        item['version'] = ''
        item['duration'] = ''
        item['publishdate'] = ''
        

        item['publishdate'] = response.xpath('//p[@class="info-release"]/text()').extract_first()
        '''
        for nodevalue in response.xpath('//article[@class="base-info"]/aside/p/text()').extract():
            if u'类型' in nodevalue:
                item['category'] = nodevalue.split('：')[1]
            if u'制式' in nodevalue:
                item['version'] = nodevalue.split('：')[1]
            if u'时长' in nodevalue:
                item['duration'] = nodevalue.split('：')[1] 
        '''

        #item['publishdate'] = response.xpath('//p[@class="info-release"]/text()').extract()
        item['image'] = u"http:" + response.xpath('//div[@class="info-poster"]/img/@src').extract_first()
        item['site'] = 'Maoyan'

        if len(response.xpath('//article[@class="m-info-crews m-info-section"]/div/div/div/div/div[1]/div[2]/text()').extract()) != 0:
            item['director'] = response.xpath('//article[@class="m-info-crews m-info-section"]/div/div/div/div/div[1]/div[2]/text()').extract_first()
        else:
            item['director'] = ''

        if len(response.xpath('//article[@class="m-info-crews m-info-section"]/div/div/div/div/div[2]/div[2]/text()').extract()) != 0:
            item['actors'] = response.xpath('//article[@class="m-info-crews m-info-section"]/div/div/div/div/div[2]/div[2]/text()').extract_first()
        else:
            item['actors'] = ''
        item['productionCompany'] = ''

        if len(response.xpath('//article[@class="production-companies m-info-section"]/div/div/div/div[2]/text()').extract()) != 0:
            productionCompanys = response.xpath('//article[@class="production-companies m-info-section"]/div/div/div/div[2]/text()').extract()
            item['productionCompany'] = ';'.join(productionCompanys) 
        else:
            item['productionCompany'] = ''

        item['distributionFirm'] = ''
        if len(response.xpath('//article[@class="distribution-firm m-info-section"]/div/div/div/div[2]/text()').extract()) != 0:
            distributionFirms =  response.xpath('//article[@class="distribution-firm m-info-section"]/div/div/div/div[2]/text()').extract()
            item['distributionFirm'] = ';'.join(distributionFirms)
        else:
            item['distributionFirm'] = ''
        if len(response.xpath('//article[@class="m-info-drama m-info-section"]/div/div[2]/text()').extract()) != 0:
            item['description'] = response.xpath('//article[@class="m-info-drama m-info-section"]/div/div[2]/text()').extract_first()
        else:
            item['description'] = ''


        boxofficeitems =  response.xpath('//div[@class="box-item"]')
        
        item['totalBoxOffice'] = ''
        item['firstweekBoxOffice'] = ''
        item['filmDayBoxOffice'] = ''

        for dataitem in boxofficeitems:
            label = dataitem.xpath('p[@class="box-desc"]/text()').extract_first()
            if u"累计票房" in label:
                try:
                    item['totalBoxOffice'] = self.decode_value(fontMapping,dataitem.xpath('p[@class="box-detail"]/span/i/text()').extract_first())
                except:
                    pass
            elif u"首周票房" in label:
                try:
                    item['firstweekBoxOffice'] = self.decode_value(fontMapping,dataitem.xpath('p[@class="box-detail"]/span/i/text()').extract_first())
                except:
                    pass
            elif u"首日票房" in label:
                try:
                    item['filmDayBoxOffice'] = self.decode_value(fontMapping,dataitem.xpath('p[@class="box-detail"]/span/i/text()').extract_first()) 
                except:
                    pass
        yield item