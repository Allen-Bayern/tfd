import scrapy
from urllib.parse import urljoin

class GaleSpider(scrapy.Spider):
    name = 'gale'
    allowed_domains = ['thefreedictionary.com']
    start_urls = ['https://medical-dictionary.thefreedictionary.com/']

    def parse(self, response):
        #pass
        