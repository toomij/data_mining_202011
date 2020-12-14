# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
import os
from dotenv import load_dotenv

class GbParsePipeline:
    def __init__(self):
        load_dotenv()

        self.db = MongoClient()[os.getenv('DATA_BASE')]

    def process_item(self, item, spider):
        if spider.db_type == 'MONGO':
            collection = self.db[spider.name]
            collection.insert_one(item)
        return item