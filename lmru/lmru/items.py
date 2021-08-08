# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
from w3lib.html import remove_tags


def convert(value):
    return float(value.replace(' ', ''))


class LmruItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field(input_processor=MapCompose(remove_tags), output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(remove_tags, convert), output_processor=TakeFirst())
    availability = scrapy.Field(input_processor=MapCompose(remove_tags), output_processor=TakeFirst())
    pictures = scrapy.Field()

    pass
