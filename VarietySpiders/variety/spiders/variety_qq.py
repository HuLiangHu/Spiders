# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import json
import re
from variety.items import VarietyItem,VarietyVideoItem
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
import logging
#http://data.video.qq.com/fcgi-bin/column/cover_list?column_id=1528&page_no=2&platform=1&version=1&cmd=list&otype=json&subtype=1&page_size=10&callback=cb_359abe456f653159

class QQSpider(scrapy.Spider):
    name = "variety_qq" 
    start_urls = ( 'http://v.qq.com/x/list/variety?istyle=-1&offset=0',
    )

    def parse(self, response):
        if re.match('^(http|https|ftp)\://v.qq.com/x/list/.*',response.url): 
            coverids = response.xpath('//ul[@class="figures_list"]/li/a/@data-float').extract()
            for cover_id in coverids:
                url = 'http://v.qq.com/detail/%s/%s.html' %(cover_id[0],cover_id)
                yield scrapy.Request(url,callback = self.detail_parse,priority=1,dont_filter = False)
            # base_url = get_base_url(response)
            #base_url ="http://v.qq.com/x/list/tv"
            pages = response.xpath('//div[@class="mod_pages"]/span/a[@class="page_num"]/@href').extract()
            for page in pages:
                #new_url = base_url+page
                # yield scrapy.Request(urljoin_rfc(base_url, page),priority=1,dont_filter = False)
                yield response.follow(page,priority=1,dont_filter = False)
        elif re.match('^(http|https|ftp)\://v.qq.com/cover.*',response.url):
            url = response.xpath('//a[@class="breadcrumb_item"]/@href').extract_first()
            cover_info = re.search('var COVER_INFO = ({[\s\S]+});',response.body_as_unicode()).group(1)
            
            variety =  VarietyItem()
            variety['name'] = re.search('title :"(.*)",',cover_info).group(1)
            variety['url'] = 'http://v.qq.com%s' %url
            variety['aid'] = re.search('id :"(.+)",',cover_info).group(1)
            variety['desc'] = re.search('brief : "(.*)",',cover_info).group(1)
            variety['cover_img'] = re.search('pic :"(.*)",',cover_info).group(1)
            if re.match('varietyDate:"(.*)",',cover_info):
                variety['lastseries'] = re.search('varietyDate:"(.*)",',cover_info).group(1) 
            variety['playStatus'] = re.search('bookTips:"(.*)",',cover_info).group(1)
            variety["website" ] =  'qq'
            request = scrapy.Request('http://sns.video.qq.com/tvideo/fcgi-bin/batchgetplaymount?low_login=1&id=%s&otype=json'%variety['aid'],priority = 1,callback = self.stats_parse)
            request.meta['tvplay'] = variety
            yield request
        
        elif re.search('v\.qq\.com\/x\/cover',response.url):
            cover_info = re.search('var COVER_INFO = ({[\s\S]+});',response.body_as_unicode()).group(1)

            variety =  VarietyItem()
            variety['name'] = re.search('title: "(.*)",',cover_info).group(1)
            variety['url'] = response.url
            variety['aid'] = re.search('id: "(.+)",',cover_info).group(1)
            variety['desc'] = re.search('brief:"(.*)",',cover_info).group(1)
            variety['cover_img'] = re.search('pic:"(.*)",',cover_info).group(1)
            if re.match('varietyDate:"(.*)",',cover_info):
                variety['lastseries'] = re.search('varietyDate:"(.*)",',cover_info).group(1) 
            variety['playStatus'] = '-'
            variety["website" ] =  'qq'
            request = scrapy.Request('http://sns.video.qq.com/tvideo/fcgi-bin/batchgetplaymount?low_login=1&id=%s&otype=json'%variety['aid'],priority = 1,callback = self.stats_parse)
            request.meta['tvplay'] = variety
            yield request
            columnid = re.search("columnid: (\d+),",cover_info).group(1)
            yield scrapy.Request('http://data.video.qq.com/fcgi-bin/column/cover_list?column_id=%s&page_no=1&platform=1&version=1&cmd=list&otype=json&subtype=1&page_size=100' %columnid,\
            meta = {'show':variety},callback = self.vidoes_parse,dont_filter = True)
        else:
            logging.error(response.url)
        
    def detail_parse(self,response):
        tvplay = VarietyItem()
        tvplay['url'] = response.url.encode("utf8")
        if re.search("id:  '(.+)'",response.text):
            tvplay["aid"] = re.search("id:  '(.+)'",response.text).group(1)
        else:
            tvplay["aid"] = re.search("detail\/\w\/([\w]+)",response.url).group(1)
        if re.search("vpic:[ ]+'(.+)';",response.text):
            tvplay['cover_img'] = re.search("vpic:  '(.+)'",response.text).group(1)
        else:
            tvplay['cover_img'] = re.search("vpic:[ ]+'(.+)'",response.text).group(1)
        if re.search("title:  '(.+)'",response.text):
            tvplay['name'] = re.search("title:  '(.+)'",response.text).group(1)
        else:
            tvplay['name'] = re.search("title:[ ]+'(.+)'",response.text).group(1)
        tvplay["website"] = 'qq'
        request = scrapy.Request('http://sns.video.qq.com/tvideo/fcgi-bin/batchgetplaymount?low_login=1&id=%s&otype=json'%tvplay['aid'],callback = self.stats_parse,priority=2,dont_filter = False)
        request.meta['tvplay'] = tvplay
        yield request

    def vidoes_parse(self,response):
        show = response.meta['show']
        jsonStr = re.search('QZOutputJson=(.+);',response.body_as_unicode()).group(1) 
        jsonObj = json.loads(jsonStr)
        page_size = int(re.search('page_size=(\d+)',response.url).group(1))
        if re.search('page_no=1&',response.url):
            total_num = jsonObj['data']['total'] 
            total_page = total_num/page_size if total_num%page_size == 0 else int(total_num/page_size) + 1  
            
            for page in range(1,total_page + 1):
                url = re.sub('page_no=1&','page_no=%d&' %page,response.url)
                yield scrapy.Request(url,meta = {'show':show},callback = self.vidoes_parse) 
        for item in jsonObj['data']['list']:
            video = VarietyVideoItem()
            video['aid'] =show['aid']
            video['vid'] = item['cid']
            video["url"] = 'http://v.qq.com/cover/%s/%s.html' %(item['cid'][0],item['cid'])
            video['albumurl'] = show['url']
            video["playdate" ] =  str(datetime.today())
            video["playCount" ] =  item['totalview']
            video["name" ] =  item['second_title']
            video["desc" ] =  item['brief']
            video["releaseDate" ] =  item['publish_date']
            video["episode" ] =  item['publish_date']
            video["website" ] =  'qq'
            video["releaseDate" ] =  ','.join(item['actor'])
            yield video
           
    def stats_parse(self,response):
        tvplay = response.meta['tvplay']
        tvplay["playdate" ] =  str(datetime.today())
        tvplay['playCount'] = int(re.search('"all":(\d+)',response.body_as_unicode()).group(1))
        yield tvplay
            