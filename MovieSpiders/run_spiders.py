from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

process = CrawlerProcess(get_project_settings())

# 'followall' is the name of one of the spiders of the project.
process.crawl('movie_hunantv')
process.crawl('movie_iqiyi')
process.crawl('movie_kankan')
process.crawl('movie_letv')
process.crawl('movie_pptv') 
process.crawl('movie_qq')
process.crawl('movie_sohu')
process.crawl('movie_youku')  


process.start() # the script will block here until the crawling is finished