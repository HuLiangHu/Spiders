# -*- coding: utf-8 -*-
# __author__ = hul  
# __date__ = 2018/10/24 下午12:32
from scrapy import cmdline
name = 'doubanteam'
name1 ='zhihutopic'
name2 ='tieba'
name3 ='tianya'
name4 ='toutiao'
name5 ='baidunews'
name6 = 'sogonews'
name7 = 'baiduinfo'
name8 ='weibo'
name9 ='weixin'
name10 ='weibocomment'
name11='weibochaohua'
name12 ='weibofans'
name13 ='weibo_youwei'
cmd = 'scrapy crawl {0} -o weibo互动-04116.csv'.format(name8)
#cmd = 'scrapy crawl {0} -o weibo话题0410.csv'.format(name11)
#cmd = 'scrapy crawl {0} -o weibo粉丝0412.csv'.format(name12)

#cmd = 'scrapy crawl {0}'.format(name13)

cmdline.execute(cmd.split())