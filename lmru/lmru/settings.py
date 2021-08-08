# Scrapy settings for lmru project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'lmru'

SPIDER_MODULES = ['spiders']
NEWSPIDER_MODULE = 'spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'lmru (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

LOG_ENABLED = True
LOG_LEVEL = 'DEBUG'

# CONCURRENT_REQUESTS = 16
#
# DOWNLOAD_DELAY = 3
#
#
# CONCURRENT_REQUESTS_PER_DOMAIN = 8
# CONCURRENT_REQUESTS_PER_IP = 8

IMAGES_STORE = 'images'

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
}


# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html

ITEM_PIPELINES = {
   'pipelines.DataBasePipeline': 300,
   'pipelines.LmruPhotosPipeline': 200,
}