import scrapy


class OmdSpider(scrapy.Spider):
    name = 'omd'
    allowed_domains = ['online-medical-dictionary.org']
    start_urls = ['https://www.online-medical-dictionary.org/']

    def parse(self, response):
        pass
