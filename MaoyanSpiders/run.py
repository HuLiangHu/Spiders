# -*- coding: utf-8 -*-
# __author__ = hul  
# __date__ = 2018/10/24 下午12:32
from scrapy import cmdline
name = 'rateinfo'

cmd = 'scrapy crawl {0} -o maoyan.csv'.format(name)
cmdline.execute(cmd.split())