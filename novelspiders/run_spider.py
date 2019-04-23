from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

process = CrawlerProcess(get_project_settings())


process.crawl('17k')
process.crawl('chuangshi_yunqi')
process.crawl('jjwxc')
process.crawl('qidian')
process.crawl('xxsy')
process.crawl('zongheng_huayu')
process.start()
