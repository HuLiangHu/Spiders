# -*- coding: utf-8 -*-
# __author__ = hul  
# __date__ = 2018/10/24 下午12:32
from scrapy import cmdline
name = 'uweel_weibo'
cmd = 'scrapy crawl {0}'.format(name)
cmdline.execute(cmd.split())