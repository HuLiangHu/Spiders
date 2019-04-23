# -*- coding: utf-8 -*-
import scrapy
import re
import json
from scrapy.linkextractors import LinkExtractor
from videosites.items import AlbumnItem
from scrapy_utils.spiders import DistributedSpider


class QQInfoSpider(DistributedSpider):
    name = 'com_qq_v_info'
    crawlid = 'default'
    allowed_domains = ['v.qq.com']
    start_urls = ['https://v.qq.com/tv/',
                  'https://v.qq.com/movie/', 
                  'https://v.qq.com/x/list/tv', 
                  'https://v.qq.com/x/list/movie',
                  'https://v.qq.com/x/rank/'
                  ]

    def parse(self, response):
        #处理列表页
        link_extractor = LinkExtractor(
            allow=(r'v\.qq\.com\/x\/list', ), restrict_css=('div.mod_pages',))
        urls = [lnk.url for lnk in link_extractor.extract_links(response)]
        for url in urls:
            yield scrapy.Request(url=url,meta = response.meta)
        #处理剧目播放页
        items_link_extractor = LinkExtractor(
            allow=(r'v\.qq\.com\/x\/cover\/\w+\.html', ), restrict_css=("ul>li.list_item",))
        urls = [lnk.url for lnk in items_link_extractor.extract_links(response)]
        for url in urls:
            request = scrapy.Request(url, meta = response.meta,callback=self.detail_parse)
            yield request

    def detail_parse(self, response):
        albumn = AlbumnItem()
        attr_val = response.xpath('//h2[@class="player_title"]/a/@href').extract_first()
        albumn['url'] = response.urljoin(attr_val)
        albumn["website"] = 'qq'
        albumn_val = re.search(r'var COVER_INFO = ({.+})',response.body_as_unicode()).group(1)
        albumn_info = json.loads(albumn_val)
        albumn["aid"] = albumn_info['id'] 
        if albumn_info['type_name'] == '电影':
            albumn['type'] = 'movie'
        elif albumn_info['type_name'] == '电视剧':
            albumn['type'] = 'tv'
        elif albumn_info['type_name'] == '综艺':
            albumn['type'] = 'variety'
        else:
            albumn['type'] = 'other'
        albumn['name'] = albumn_info['title']
        albumn['name_en'] = albumn_info.get('title_en',None)
        albumn['series_name']= albumn_info.get('series_name',None)
        albumn['series_num']= albumn_info.get('series_num',None)
        albumn['area'] = albumn_info.get('area_name',None)
        albumn['desc'] =  albumn_info.get('description',None)
        albumn['episodes'] =  albumn_info.get('episode_all',None)
        albumn['directors'] =  albumn_info.get('director',None)
        albumn['actors'] =  albumn_info.get('leading_actor',None)
        albumn['cover_img'] =  albumn_info.get('vertical_pic_url',None)
        albumn['cover_img_sm'] =  albumn_info.get('horizontal_pic_url',None)
        albumn['playStatus'] = albumn_info.get('update_notify_desc',None)
        albumn['genre'] = albumn_info.get('main_genre',None)
        albumn['tags'] = albumn_info.get('tag',None)
        albumn['lastepisode'] = albumn_info.get('episode_updated',None)
        albumn['additional_infos'] = {}
        albumn['releaseDate'] = albumn_info.get('publish_date',None)
        albumn['alias'] = albumn_info.get('alias',None)
        yield albumn
