# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
# @Time : 2017/1/1 17:51

from scrapy import cmdline
name = 'tiebastats'
cmd = 'scrapy crawl {0}'.format(name)
cmdline.execute(cmd.split())