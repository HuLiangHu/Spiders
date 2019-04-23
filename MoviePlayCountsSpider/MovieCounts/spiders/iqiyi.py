# -*- coding: utf-8 -*-
import scrapy
import json
import re
from scrapy.selector import Selector
from datetime import datetime
from MovieCounts.items import MoviecountsItem
import requests
from lxml import etree


def get_comingmoviename():
    doubanwill = 'https://movie.douban.com/coming'
    res = requests.get(doubanwill).text
    html = etree.HTML(res)
    name = html.xpath('//div[@class="grid-16-8 clearfix"]/div/table/tbody/tr/td/a/text()')
    return name


class IQiyiSpider(scrapy.Spider):

    name = "iqiyi"
    moviename=get_comingmoviename()
    starturls = 'http://search.video.iqiyi.com/o?channel_name=%E7%94%B5%E5%BD%B1&if=html5&pageNum=1&pageSize=1&limit=20&category=&timeLength=0&releaseDate=&key={}&start=1&threeCategory=&u=b1m6wyyzos2knlxe698e1qqb&qyid=b1m6wyyzos2knlxe698e1qqb&pu=2125035081&video_allow_3rd=1&intent_result_number=10&intent_category_type=1&vfrm=2-3-0-1&_=1531981545941'
    dataapi='http://mixer.video.iqiyi.com/jp/recommend/videos?albumId={}&channelId=10&cookieId=0ce767741c70369d933a80e5d0dd7131&withRefer=true&area=zebra&size=10&type=video&pru=&locale=&userId=&playPlatform=PC_QIYI&isSeriesDramaRcmd='
    def start_requests(self):
        # self.server = connection.from_settings(self.settings)
        for name in self.moviename:
            url = self.starturls.format(name)
            yield scrapy.Request(url)


    def parse(self, response):
        result = json.loads(response.text)
        if result['data']['code'] == 0:

            if len(result['data']['docinfos'])>0:
                albumn = result['data']['docinfos'][0]['albumDocInfo']
                if 'prevues' in albumn:
                    for item in albumn['prevues']:
                        video = MoviecountsItem()
                        video["title"]=item["itemTitle"]
                        #video["view_count"]=i["playCount"]
                        video["comefrom"]="iqiyi"
                        video["datetime"]=str(datetime.now())
                        video["url"]=item["itemLink"]
                        video["updatetime"]=str(datetime.today())
                        yield scrapy.Request('https://pcw-api.iqiyi.com/video/video/hotplaytimes/%s' %item['tvId'], meta={"video":video},callback=self.parse_playcount)

    def parse_playcount(self,response):
        video = response.meta['video']
        for i in json.loads(response.text)['data']:
            video['view_count'] = i['hot']
            yield video

    def parse_detail(self,response):
        tvid=response.xpath('//div[@data-player-tvid]/@data-player-tvid').extract_first()
        next_url=self.dataapi.format(tvid)
        yield scrapy.Request(next_url,callback=self.parse_grade)


    def parse_grade(self,response):
        data = re.findall(r'var tvInfoJs=(.*)',response.text)[0]

        jsondata = json.loads(data)
        for i in jsondata["mixinVideos"]:
            item = MoviecountsItem()
            item["title"]=i["name"]
            item["view_count"]=i["playCount"]
            item["comefrom"]="aiqiyi"
            item["datetime"]=str(datetime.now())
            item["url"]=i["url"]
            #item["updatetime"]=str(datetime.today())
            yield item
















