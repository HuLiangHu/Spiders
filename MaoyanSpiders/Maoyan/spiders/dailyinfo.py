# -*- coding: utf-8 -*-
import time
from scrapy.spiders import Spider
from Maoyan.items import DailyBoxOfficeItem
import re
import json
import scrapy
from datetime import date, datetime, timedelta
from Maoyan.fonthelper import *
from scrapy.selector import Selector

class DailyInfoSpider(Spider):
    name = "dailyinfo"
    start_urls = []
    fontMapping = []
    def __init__(self):
        super(DailyInfoSpider,self).__init__()
        self.start_urls = self.get_start_urls() #['http://piaofang.maoyan.com/?date=2012-01-08'] #
    def get_start_urls(self):
        urls = []
        for i in range(1,2):
            urls.append('http://piaofang.maoyan.com/dayoffice?date=%s&cnt=10' %str(date.today() - timedelta(days=i)))
        return urls
    def parse(self, response):
        jsonData = json.loads(response.body_as_unicode())
        ticketList = Selector(text=jsonData['ticketList']) 
        matchs = re.search('data:application\/font-\w+;charset=utf-8;base64,(.*)\) format\("(\w+)"\);',jsonData['fontsUrl'])
        b64font = matchs.group(1)
        fontMapping = extract_fonts(b64font)
        if re.search('date=([\d-]+)', response.url):
            date = re.search('date=([\d-]+)', response.url).group(1)
        unicodeStr =  response.xpath('//span[@id="ticket_count"]/i/text()').extract_first()
        if unicodeStr:
            totalBoxoffice = self.decode_value(fontMapping,unicodeStr)
        else:
            totalBoxoffice =  response.xpath('//span[@id="ticket_count"]/text()').extract_first().strip()
        for item in ticketList.xpath('//ul'):
            maoyanid = re.search('\/movie\/(\d+)',item.xpath('@data-com').extract_first()).group(1)
            name = item.xpath('li[@class="c1"]/b/text()').extract_first()
            showDay = item.xpath('li[@class="c1"]/em/text()').extract_first()
            unicodeStr = item.xpath('li[@class="c1"]/em/i/text()').extract_first()
            if unicodeStr:
                summaryBoxOffice = self.decode_value(fontMapping,unicodeStr)
            else:
                summaryBoxOffice = item.xpath('li[@class="c1"]/em/text()').extract_first().strip()
            unicodeStr = item.xpath('li[@class="c2 "]/b/i/text()').extract_first()
            if unicodeStr:
                dailyBoxOffice = self.decode_value(fontMapping,unicodeStr)
            else:
                dailyBoxOffice = item.xpath('li[@class="c2 "]/b/text()').extract_first().strip()
            unicodeStr = item.xpath('li[@class="c3 "]/i/text()').extract_first()
            if unicodeStr:
                boxofficePer = self.decode_value(fontMapping,unicodeStr)
            else:
                boxofficePer = item.xpath('li[@class="c3 "]/text()').extract_first().strip()
            unicodeStr = item.xpath('li[@class="c4 "]/i/text()').extract_first()
            if unicodeStr:
                screeningsPer = self.decode_value(fontMapping,unicodeStr)
            else:
                screeningsPer = item.xpath('li[@class="c4 "]/text()').extract_first().strip()
            unicodeStr = item.xpath('li[@class="c5 "]/span/i/text()').extract_first()
            if unicodeStr:
                attendance = self.decode_value(fontMapping,unicodeStr)
            else:
                attendance = item.xpath('li[@class="c5 "]/span/text()').extract_first().strip()
            
            item = DailyBoxOfficeItem()
            
            item['day']=date
            item['maoyanid']=maoyanid
            item['name']=name
            item['showDay']=showDay
            item['summaryBoxOffice']=summaryBoxOffice
            item['totalBoxOffice']=totalBoxoffice
            item['dailyBoxOffice']=dailyBoxOffice
            item['boxofficePer']=boxofficePer
            item['screeningsPer']=screeningsPer
            item['attendance']=attendance 
            
            yield item

    def decode_value(self,fontMapping,rawdata):
        charts = []
        for chart in rawdata:
            decimalCode = ord(chart)
            if str(decimalCode) in fontMapping: 
                charts.append(str(fontMapping[str(decimalCode)] ))
            else:
                charts.append(chart)
        return ''.join(charts)
