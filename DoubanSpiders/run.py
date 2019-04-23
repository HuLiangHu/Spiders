import scrapy
from scrapy.crawler import CrawlerProcess
from douban.spiders.doubanmovieinfo import DoubanMovieInfoSpider
from douban.spiders.movies import DoubanMoviesSpider
from douban.spiders.movieinfo import MovieInfoSpider
from scrapy.utils.project import get_project_settings
process = CrawlerProcess(get_project_settings())
process.crawl(DoubanMovieInfoSpider)
#process.crawl(AudiencesSpider)
process.start() # the script will block here until all crawling jobs are finished