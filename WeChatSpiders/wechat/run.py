# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
# @Time : 2017/1/1 17:51
# @Author : woodenrobot
from scrapy import cmdline
#name = 'weibostats'
name ='wechatindex_new'
cmd = 'scrapy crawl {0} -o wechatindex.csv'.format(name)
#cmd = 'scrapy crawl {0} -o weiboindexid.csv'.format(name1)
cmdline.execute(cmd.split())