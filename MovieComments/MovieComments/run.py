# -*- coding: utf-8 -*-
# __author__ = hul  
# __date__ = 2018/9/5 下午9:27
from scrapy import cmdline
name = 'iqiyi'
name1 ='iqiyi_old'
name2 = 'sohu'
name3 ='youku'
name4 = 'tencent'
name5 ='pptv'
name6 ='DMtencent'
name7 ='DMiqiyi'
name8='mgtv'
name9 ='DMyouku'
name10 ='letv'
cmd = 'scrapy crawl {0}'.format(name)
cmdline.execute(cmd.split())