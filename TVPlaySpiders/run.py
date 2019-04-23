import scrapy
from scrapy.crawler import CrawlerProcess
from webplay.spiders.tv_hunantv import HunanTVSpider
from webplay.spiders.tv_iqiyi import IQiyiSpider
from webplay.spiders.tv_kankan import *
from webplay.spiders.tv_letv import *
from webplay.spiders.tv_pptv import *
from webplay.spiders.tv_qq import *
from webplay.spiders.tv_sohu import *
from webplay.spiders.tv_tudou import *
from webplay.spiders.tv_youku import *

from scrapy.utils.project import get_project_settings
process = CrawlerProcess(get_project_settings())

process.crawl(HunanTVSpider)
process.crawl(IQiyiSpider)
process.crawl(KankanSpider)
process.crawl(LetvSpider)
process.crawl(PPTVSpider)
process.crawl(QQSpider)
process.crawl(SohuSpider)
process.crawl(TudouSpider)
process.crawl(YoukuSpider)
process.start() # the script will block here until all crawling jobs are finished