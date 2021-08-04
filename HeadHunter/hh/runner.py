from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from spiders.hh_spider import HhSpiderSpider
from spiders.sj_spider import SjSpiderSpider
import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(HhSpiderSpider)   # modified spider for head hunter
    process.crawl(SjSpiderSpider)   # new spider for superjobs.ru
    process.start()
