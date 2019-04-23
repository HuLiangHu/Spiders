# -*- coding: utf-8 -*-
import scrapy
import re
import json
from scrapy.linkextractors import LinkExtractor
from videosites.items import AlbumnItem


class YoukuInfoSpider(scrapy.Spider):
    name = 'com_youku_info'
    crawlid = 'default'
    allowed_domains = ['youku.com']
    start_urls = ['https://tv.youku.com/',
                 'https://movie.youku.com/', 
                  'https://list.youku.com/category/show/c_97_r__u_2_s_1_d_1.html', 
                 'https://list.youku.com/category/show/c_97_u_1_s_1_d_1.html', 
                 'https://list.youku.com/category/show/c_96_s_1_d_1_u_1.html', 
                 'https://top.youku.com/rank/detail/?m=96&type=1',
                  'https://top.youku.com/rank/detail/?m=97&type=1'
                  ]
    custom_settings = {
        'DOWNLOAD_DELAY':0.5
    }
    def parse(self, response):
        #处理列表页
        link_extractor = LinkExtractor(
            allow=(r'list\.youku\.com\/category\/show', ), restrict_css=('div.yk-pager>ul','div.yk-filter-panel>div:nth-child(4)',))
        urls = [lnk.url for lnk in link_extractor.extract_links(response)]
        for url in urls:
            yield scrapy.Request(url=url)
        #处理剧目播放页
        items_link_extractor = LinkExtractor(
            allow=(r'v\.youku\.com\/v_show\/id_', ),restrict_css=('div.box-series','div.s-main','div.exp-Rank',))
        urls = [lnk.url for lnk in items_link_extractor.extract_links(response)]
        for url in urls:
            request = scrapy.Request(url, callback=self.detail_url_parse)
            yield request
        #剧目详细页面
    def detail_url_parse(self,response):
        detail_url = response.xpath('//div[@class="tvinfo"]/h2/a/@href').extract_first()
        yield response.follow(detail_url,priority=2,callback=self.detail_parse)

    def detail_parse(self, response):
        albumn = AlbumnItem()
        albumn["url"] =  response.url
        albumn["website"] = 'youku'
        albumn["aid"] = re.search(r'id_(.*).html',response.url).group(1)
        albumn_type = response.xpath('//div[@class="p-base"]/ul/li[@class="p-row p-title"]/a/text()').extract_first()
        if albumn_type == '电影':
            albumn['type'] = 'movie'
        elif albumn_type == '剧集':
            albumn['type'] = 'tv'
        elif albumn_type == '综艺':
            albumn['type'] = 'variety'
        else:
            albumn['type'] = 'other'
        albumn['name'] = response.xpath('//div[@class="p-base"]/ul/li[@class="p-row p-title"]/text()').extract_first()[1:]
       
        albumn['area'] = response.xpath('//div[@class="p-base"]/ul/li[contains(., "地区")]/a/text()').extract_first()
        albumn['desc'] =  response.xpath('//div[@class="p-base"]/ul/li[@class="p-row p-intro"]/span[@class="text"]/text()').extract_first()
        
        albumn['directors'] = response.xpath('//div[@class="p-base"]/ul/li[contains(., "导演")]/a/text()').extract()
        albumn['actors'] =  response.xpath('//div[@class="p-base"]/ul/li[contains(., "主演")]/a/text()').extract()
        albumn['cover_img'] = response.xpath('//div[@class="mod fix"]/div/div/div[@class="p-thumb"]/img/@src').extract_first()
        albumn['genre'] = response.xpath('//div[@class="p-base"]/ul/li[contains(., "类型")]/a/text()').extract_first()
        albumn['tags'] = response.xpath('//div[@class="p-base"]/ul/li[contains(., "类型")]/a/text()').extract()
        if re.search(r'doubanId:"(\d+)"',response.body_as_unicode()):
            doubanid = re.search(r'doubanId:"(\d+)"',response.body_as_unicode()).group(1)
            albumn['additional_infos'] = {'doubanid':doubanid}
        albumn['releaseDate'] = response.xpath('//div[@class="p-base"]/ul/li/span[@class="pub"]/text()').extract_first()
        albumn['alias'] = response.xpath('//div[@class="p-base"]/ul/li[@class="p-alias"]/@title').extract_first()
       
        play_info = response.xpath('//div[@class="p-base"]/ul/li[@class="p-row p-renew"]/text()').extract_first()
        if re.search(r'共(\d+)集',str(play_info)):
            total_episodes = re.search(r'共(\d+)集',str(play_info)).group(1)
            albumn['episodes'] =  total_episodes
        if re.search(r'更新至(\d+)集',str(play_info)):
            last_episode = re.search(r'更新至(\d+)集',str(play_info)).group(1)
            albumn['lastepisode'] =  last_episode
        albumn['playStatus'] = play_info
        yield albumn