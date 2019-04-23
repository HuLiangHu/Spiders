import scrapy
from scrapy.crawler import CrawlerProcess



from scrapy.utils.project import get_project_settings

from MovieComments.spiders.iqiyi import IqiyiSpider
from MovieComments.spiders.mgtv import MgtvSpider
from MovieComments.spiders.tencent import TencentSpider
from MovieComments.spiders.youku import YoukuSpider

process = CrawlerProcess(get_project_settings())
process.crawl(IqiyiSpider)
process.crawl(YoukuSpider)
process.crawl(TencentSpider)
process.crawl(MgtvSpider)
process.start() # the script will block here until all crawling jobs are finished