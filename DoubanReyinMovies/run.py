import scrapy
from scrapy.crawler import CrawlerProcess
from douban.spiders.doubangrade import DoubanMoviesSpider
from scrapy.utils.project import get_project_settings
process = CrawlerProcess(get_project_settings())
process.crawl(DoubanMoviesSpider)
#process.crawl(AudiencesSpider)
process.start() # the script will block here until all crawling jobs are finished