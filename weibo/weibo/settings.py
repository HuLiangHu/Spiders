# Scrapy settings for scrapy_weibo project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#
import os
BOT_NAME = 'weibo'

SPIDER_MODULES = ['weibo.spiders']
NEWSPIDER_MODULE = 'weibo.spiders'



# redis config
REDIS_HOST = '10.10.121.66'
REDIS_PORT = 6379
 
# start MySQL database configure 
# setting
MYSQL_HOST = os.environ['MYSQL_HOST'] if 'MYSQL_HOST' in os.environ else  ''
MYSQL_DBNAME = os.environ['MYSQL_DBNAME'] if 'MYSQL_DBNAME' in os.environ else  'newmedia_db'
MYSQL_USER = os.environ['MYSQL_USER'] if 'MYSQL_USER' in os.environ else ''
MYSQL_PASSWD =os.environ['MYSQL_PASSWD'] if 'MYSQL_PASSWD' in os.environ else  '' 
MYSQL_PORT = os.environ['MYSQL_PORT'] if 'MYSQL_PORT' in os.environ else  3306

# pipelines config
ITEM_PIPELINES = { 
   'weibo.pipelines.MyCSVPipeline':200
}

LOG_LEVEL = 'ERROR'
#DOWNLOAD_DELAY = 10

#TIME_DELTA = 30

# bootstrap from file (item.txt) or from db
BOOTSTRAP = 'file'

# how many feeds can fetch from a item
FEED_LIMIT = 30000000

MONGOD_HOST = '10.10.121.66'
MONGOD_PORT = 27017

FEED_EXPORT_ENCODING = 'UTF-8'

FEED_EXPORTERS = {
    'csv': 'weibo.exporters.MyCsvItemExporter',
}