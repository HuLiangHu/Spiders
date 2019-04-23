import scrapy
from scrapy import signals
from scrapy.crawler import CrawlerProcess 
from scrapy.xlib.pydispatch import dispatcher
from scrapy.utils.project import get_project_settings 
from variety.spiders.variety_kankan import KankanSpider
from variety.spiders.variety_tudou import TudouSpider
from variety.spiders.variety_hunantv import HunanTVSpider
from variety.spiders.variety_iqiyi import IQiyiSpider
from variety.spiders.variety_letv import LetvSpider
from variety.spiders.variety_pptv import PPTVSpider
from variety.spiders.variety_qq import QQSpider
from variety.spiders.variety_sohu import SohuSpider
from variety.spiders.variety_youku import YoukuSpider

process = CrawlerProcess(get_project_settings())

def handleSpiderIdle(spider):
    '''Handle spider idle event.''' # http://doc.scrapy.org/topics/signals.html#spider-idle
    print('\nSpider idle: %s. Restarting it... ' % spider.name)
    #spider.schedule_next_requests()
    '''
    for url in spider.start_urls: # reschedule start urls
        spider.crawler.engine.crawl(Request(url, dont_filter=True), spider)
    '''

# 'followall' is the name of one of the spiders of the project.
process.crawl(KankanSpider)
process.crawl(TudouSpider)
process.crawl(HunanTVSpider)
process.crawl(IQiyiSpider)
process.crawl(LetvSpider)
process.crawl(PPTVSpider)
process.crawl(QQSpider)
process.crawl(SohuSpider)
process.crawl(YoukuSpider)

dispatcher.connect(handleSpiderIdle, signals.spider_idle)
process.start() # the script will block here until the crawling is finished