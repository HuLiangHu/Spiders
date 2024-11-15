# -*- coding: utf-8 -*-

# Scrapy settings for tieba project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/lat est/topics/spider-middleware.html
import os
from .zz_proxies import get_ip
IPLIST =get_ip.get_iplist()

BOT_NAME = 'weibo'

SPIDER_MODULES = ['weibo.spiders']
NEWSPIDER_MODULE = 'weibo.spiders'

# start MySQL database configure setting
MYSQL_HOST = os.environ['MYSQL_HOST'] if 'MYSQL_HOST' in os.environ else  ''
MYSQL_DBNAME = os.environ['MYSQL_DBNAME'] if 'MYSQL_DBNAME' in os.environ else ''
MYSQL_USER = os.environ['MYSQL_USER'] if 'MYSQL_USER' in os.environ else ''
MYSQL_PASSWD = os.environ['MYSQL_PASSWD'] if 'MYSQL_PASSWD' in os.environ else ''
MYSQL_PORT = os.environ['MYSQL_PORT'] if 'MYSQL_PORT' in os.environ else  3306
# # end of MySQL database configure setting
# DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# # Kafka server information
# KAFKA_HOSTS = os.environ['KAFKA_HOSTS'].split(',') if 'KAFKA_HOSTS' in os.environ else ['emr-worker-1.cluster-54652:9092','emr-worker-2.cluster-54652:9092','emr-worker-3.cluster-54652:9092']
# KAFKA_TOPIC = os.environ['KAFKA_TOPIC']  if 'KAFKA_TOPIC' in os.environ else 'spider.crawled_weibo'
#KAFKA_APPID_TOPICS = False
# base64 encode the html body to avoid json dump errors due to malformed text
#KAFKA_BASE_64_ENCODE = False
# KAFKA_PRODUCER_BATCH_LINGER_MS = 25  # 25 ms before flush
# KAFKA_PRODUCER_BUFFER_BYTES = 4 * 1024 * 1024  # 4MB before blocking

# start Redis configure setting
#REDIS_HOST = '10.168.181.131'
#REDIS_HOST = '121.41.40.219'
#REDIS_PORT = 6379
# REDIS_URL = 'redis://127.0.0.1:6379'
#REDIS_URL = 'redis://user:pass@hostname:9001'
# end of Redis  configure setting

# Enables scheduling storing requests queue in redis.
#SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# Don't cleanup redis queues, allows to pause/resume crawls.
SCHEDULER_PERSIST = True

RETRY_TIMES = 1

SCHEDULER_IDLE_BEFORE_CLOSE = 10

# Schedule requests using a priority queue. (default)
#SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderPriorityQueue'
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'tieba (+http://www.yourdomain.com)'

LOG_LEVEL = os.environ['LOG_LEVEL'] if 'LOG_LEVEL' in os.environ else 'DEBUG'
#LOG_FILE = 'log.txt'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS=32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY=3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN=16
#CONCURRENT_REQUESTS_PER_IP=16

# Disable cookies (enabled by default)
#COOKIES_ENABLED=False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED=False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'weibo.middlewares.MyCustomSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'weibo.middlewares.MyCustomDownloaderMiddleware': 543,
#}
DOWNLOADER_MIDDLEWARES = {
    'weibo.middlewares.RandomProxy': 90,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 100,
    'weibo.middlewares.RandomUserAgent': 200
}
# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.telnet.TelnetConsole': None,
#}
# DOWNLOADER_DELAY = 1
# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'weibo.pipelines.MySqlPipeline': 300,
}
FEED_EXPORT_ENCODING ="utf-8-sig"
#
#MAIL_FROM:'webplay_MDS@data4media.com'
COOKIES = [
    'BDUSS=3dTS2ZyfjRhbkhwdG55SXRCcHJRVk82a0Z2cXYtVFNLT3FZZXdReWY4ZUUwNTFjQVFBQUFBJCQAAAAAAAAAAAEAAABBLvdUybPMssnPtcS83NfTucQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIRGdlyERnZcd',
    'BDUSS=Hd3QWRva0RLNENMR0s5MUJHbnpJYm9oSzNaVnF-c2ZFQWNjZUhLfkV3bkYwcDVjQVFBQUFBJCQAAAAAAAAAAAEAAADC2h02ze3N7WRodQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMVFd1zFRXdcb',
    'BDUSS=s0LTl2NTNVUTJKMmNZTHV3UGhXd0J6ZWk3TXRZa3ZyalpndHh1dW5yWmtEWjViQVFBQUFBJCQAAAAAAAAAAAEAAACVe8E9uf608873uc-5~gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGSAdltkgHZbbW',
    'BDUSS=WVKUEVOYmVlOGllN2hhTVZ-S0NRanlEVDdQRG5DM2lKSkJqNUx6aUdnNWUxNTVjQUFBQUFBJCQAAAAAAAAAAAEAAADEHHAk0KG~8NfTMjIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAF5Kd1xeSndcV',
    'BDUSS=VRsS2Z3LU5RNDl1bWt4bUl1fmN-S29XckVOSFF1bkZ5czl6NG9uWUdoTmkySjVjQUFBQUFBJCQAAAAAAAAAAAEAAAAE1KqUz8K~zsHLyKXFtsbGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGJLd1xiS3dca',
    'BDUSS=Ec3en41MDd-ajY2QnVMeDFHbXp-VDJ0TEd-bU8tbEJVSUVYcXlrMklmclUyWjVjQVFBQUFBJCQAAAAAAAAAAAEAAABA2qoDZGF4aW9uZzgwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANRMd1zUTHdcM'
]

#
#STATS_CLASS = 'scrapy.statscollectors.MemoryStatsCollector'
#
# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# NOTE: AutoThrottle will honour the standard settings for concurrency and delay
#AUTOTHROTTLE_ENABLED=True
# The initial download delay
#AUTOTHROTTLE_START_DELAY=5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY=60
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG=False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED=True
#HTTPCACHE_EXPIRATION_SECS=0
#HTTPCACHE_DIR='httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES=[]
#HTTPCACHE_STORAGE='scrapy.extensions.httpcache.FilesystemCacheStorage'

