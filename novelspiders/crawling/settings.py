# -*- coding: utf-8 -*-
from .zz_proxies import get_ip

BOT_NAME = 'crawling'

SPIDER_MODULES = ['crawling.spiders']
NEWSPIDER_MODULE = 'crawling.spiders'
REDIS_HOST = ''
SC_LOG_STDOUT = True
SC_LOG_JSON = False
SC_LOG_DIR = '/var/scrapy-cluster'
SC_LOG_LEVEL = 'DEBUG'

HTTPCACHE_ENABLED = False
COOKIES_ENABLED=False
RETRY_ENABLED =True
REFERER_ENABLED = True
QUEUE_HITS = 60
QUEUE_WINDOW = 10
RETRY_TIMES =5
DOWNLOADER_DELAY=2
MYSQL_HOST = ''
MYSQL_DBNAME = ''
MYSQL_USER = ''
MYSQL_PASSWD = ''
MYSQL_PORT = 3306
DOWNLOAD_TIMEOUT =30
WEIBO_TOKEN = ''
ITEM_PIPELINES = {
    'crawling.pipelines.MySqlPipeline': 99
}
# DOWNLOADER_MIDDLEWARES = {
#     'crawling.middleware.RandomUserAgent': 100,
#     'crawling.middleware.RandomProxy': 150,
#     'crawling.middleware.ProcessAllExceptionMiddleware':151
# }
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.54 Safari/536.5'
#USER_AGENT ='readx/7.2.1 (iPhone; iOS 12.0; Scale/2.00)'
RETRY_HTTP_CODES=[302,301,403]
IPLIST=get_ip.get_iplist()

