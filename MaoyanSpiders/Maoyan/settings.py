# -*- coding: utf-8 -*-

# Scrapy settings for Maoyan project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
from zz_proxy import get_ip
IPLIST=get_ip.get_iplist()
import os

BOT_NAME = 'Maoyan'

SPIDER_MODULES = ['Maoyan.spiders']
NEWSPIDER_MODULE = 'Maoyan.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'Maoyan (+http://www.yourdomain.com)'
MYSQL_HOST = os.environ['MYSQL_HOST'] if 'MYSQL_HOST' in os.environ else  'mysql.crotondata.cn'
MYSQL_DBNAME = os.environ['MYSQL_DBNAME'] if 'MYSQL_DBNAME' in os.environ else 'media'
MYSQL_USER = os.environ['MYSQL_USER'] if 'MYSQL_USER' in os.environ else ''
MYSQL_PASSWD = os.environ['MYSQL_PASSWD'] if 'MYSQL_PASSWD' in os.environ else ''
MYSQL_PORT = os.environ['MYSQL_PORT'] if 'MYSQL_PORT' in os.environ else  3306
# Obey robots.txt rules
# ROBOTSTXT_OBEY = True
# Obey robots.txt rules
# ROBOTSTXT_OBEY = True
#REDIS_HOST = 'redis'
#REDIS_PORT = 6379
 
# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'Maoyan.middlewares.MyCustomSpiderMiddleware': 543,
# }
User_Agent='Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'Maoyan.middlewares.MyCustomDownloaderMiddleware': 543,
# }
DOWNLOADER_MIDDLEWARES = {
    'Maoyan.middlewares.RandomUserAgent': 100,
    'Maoyan.middlewares.RandomProxy': 150,
    'Maoyan.middlewares.ProcessAllExceptionMiddleware':151
}
# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#     # 'Maoyan.pipelines.MaoyanPipeline': 300,
#     'Maoyan.pipelines.MySqlPipeline': 300,
# }
#LOG_LEVEL = 'ERROR'
#DOWNLOAD_DELAY = 1
#LOG_FILE = 'log.txt'
# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
