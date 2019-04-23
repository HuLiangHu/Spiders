import scrapy
from scrapy.crawler import CrawlerProcess
from MovieCounts.spiders.iqiyi import IQiyiSpider
#from MovieCounts.spiders.letv import LetvSpider
#from MovieCounts.spiders.souhu import SouhuSpider
from MovieCounts.spiders.qq import QQSpider
from MovieCounts.spiders.youku import YoukuSpider



from scrapy.utils.project import get_project_settings
process = CrawlerProcess(get_project_settings())

process.crawl(IQiyiSpider)
#process.crawl(LetvSpider)
#process.crawl(SouhuSpider)
process.crawl(QQSpider)
process.crawl(YoukuSpider)
process.start() # the script will block here until all crawling jobs are finished