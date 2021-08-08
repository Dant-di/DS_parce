# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


import scrapy
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient


class DataBasePipeline(object):

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client['parsed_jobs']

    def process_item(self, item, spider):
        collection = self.mongobase[spider.name]
        collection.insert_one(item)

        return item


class LmruPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['pictures']:
            for img in item['pictures']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item['pictures'] = [itm[1] for itm in results if itm[0]]
        return item