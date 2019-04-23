# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
# @Time : 2017/1/1 17:51
# @Author : woodenrobot
from scrapy import cmdline
name = 'zongheng_huayu'
#cmd = 'scrapy crawl {0} -o zongheng_huayu.csv'.format(name)
cmd = 'scrapy crawl {0}'.format(name)
cmdline.execute(cmd.split())