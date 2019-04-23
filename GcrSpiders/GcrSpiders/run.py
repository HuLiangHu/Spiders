# -*- coding: utf-8 -*-
# __author__ = hul  
# __date__ = 2018/11/2 下午4:34
from scrapy import cmdline
name = 'kuaikan'

cmd = 'scrapy crawl {0} -o kuaikan.csv'.format(name)
cmdline.execute(cmd.split())