# -*- coding: utf-8 -*-
# __author__ = hul  
# __date__ = 2018/9/3 上午11:41
from scrapy import cmdline
name = 'movie'
# name = 'doubanbookinfo'
# name = 'book'
cmd = 'scrapy crawl {0} -o douban.csv'.format(name)
# cmd = 'scrapy crawl {0}'.format(name)
cmdline.execute(cmd.split())