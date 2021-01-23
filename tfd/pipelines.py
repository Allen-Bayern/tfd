# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json

class TfdPipeline:

    def open_spider(self, spider):
        self.file = open('tfd/spiders/data/tfd.json', 'w', encoding = 'utf-8')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        dictItem = dict(item)
        strItem = json.dumps(dictItem, ensure_ascii = False) + ',\n'
        self.file.write(strItem)
        return item