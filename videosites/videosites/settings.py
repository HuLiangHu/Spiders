# -*- coding: utf-8 -*-

# Scrapy settings for videosites project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'videosites'

SPIDER_MODULES = ['videosites.spiders']
NEWSPIDER_MODULE = 'videosites.spiders'


###----scrapy-utils config----### 
# Kafka Config
KAFKA_HOSTS = ['']
KAFKA_PRODUCER_BATCH_LINGER_MS = 5000
KAFKA_PRODUCER_BUFFER_BYTES = 100*1024
KAFKA_TOPIC = 'spider-com-douban-movie-comments-dev' 
# Redis Config
REDIS_HOST = 'croton-redis-dev.redis.rds.aliyuncs.com'
REDIS_PORT = 6379
REDIS_DB = 1
REDIS_PASSWORD = None
DUPEFILTER_DEBUG = False
DUPEFILTER_CLASS = "scrapy_utils.dupefilter.RedisDupeFilter"
SCHEDULER_DUPEFILTER_KEY = "%(spider)s:dupefilter"
DUPEFILTER_TIMEOUT = 10#5*60
SCHEDULER_FLUSH_ON_START = False
SCHEDULER = "scrapy_utils.scheduler.DistributedScheduler"
SCHEDULER_QUEUE_CLASS = 'scrapy_utils.queue.RedisPriorityQueue'
SCHEDULER_PERSIST = True


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'videosites (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False
LOG_LEVEL = 'DEBUG'
# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'videosites.middlewares.VideositesSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'videosites.middlewares.VideositesDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'videosites.pipelines.VideoSitesPipeline':200,
    'scrapy_utils.pipelines.KafkaPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Local Overrides
# ~~~~~~~~~~~~~~~

try:
    from .settings_local import *
except ImportError:
    pass