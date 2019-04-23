from scrapy import cmdline
name = 'search'
#cmd = 'scrapy crawl {0} -o zongheng_huayu.csv'.format(name)
cmd = 'scrapy crawl {0}'.format(name)
cmdline.execute(cmd.split())

