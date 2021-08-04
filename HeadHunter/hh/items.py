# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HhItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field()
    min_salary = scrapy.Field()
    max_salary = scrapy.Field()
    vacancy_link = scrapy.Field()
    source = scrapy.Field()

    pass
