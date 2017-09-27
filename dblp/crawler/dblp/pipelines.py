# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo


class MongoDBPipeline(object):

    def __init__(self, settings):
        self.mongo_uri = settings['MONGODB_URL']
        self.mongo_db = settings['MONGODB_DB']
        self.mongo_coll = settings['MONGODB_COLLECTION']

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls(crawler.settings)
        return s

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.collection = self.db[self.mongo_coll]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.collection.find_one_and_update(
            {
                "title": item["title"],
                "year": item["year"],
                "_type": item["_type"],
                "_pname": item["_pname"],
                "_dname": item["_dname"]
            },
            {"$set": dict(item)},
            upsert=True
        )
        # spider.logger.info("add {}".format(item))
        return item
