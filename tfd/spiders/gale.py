import scrapy
from urllib.parse import urljoin
from ..items import TfdItem
import re

class GaleSpider(scrapy.Spider):
    name = 'gale'
    allowed_domains = ['thefreedictionary.com']
    start_urls = ['https://medical-dictionary.thefreedictionary.com/']

    def getWordList(self):
        with open('files/mwd.txt', 'r', encoding='utf-8') as file:
            wl = file.readlines()
            wordList = set() # 去重
            for i in wl:
                i = i.replace('\n', '')
                wordList.add(i)
        
        return sorted(list(wordList)) # 按字母顺序排好
    
    def dropTags(self, text):  # 可以用于除去HTML标签的函数
        pattern = re.compile(r"<[^>]+>", re.S)
        res = pattern.sub('', text)
        return res

    def parse(self, response):
        #pass
        wordList = self.getWordList()
        for word in wordList:
            newUrl = urljoin('https://medical-dictionary.thefreedictionary.com/impotence', word)
            yield scrapy.Request(newUrl, callback=self.getMeanings, dont_filter=True)
    
    def getMeanings(self, response):
        item = TfdItem()
        sources = response.xpath('//div[@id="Definition"]/section/@data-src').getall()
        if 'gem' not in sources:
            yield None
        elif 'gem' in sources:
            gem = response.xpath('//section[@data-src="gem"]')
            item['word'] = gem.xpath('./h2/text()').get()
            if gem.xpath('./div[@class="runseg"]'): # 如果底下有很多节点
                # 分析实例：https://medical-dictionary.thefreedictionary.com/bronchitis
                # 还得写正则啊
                nodes = gem.xpath('./child:*')
                obj = dict()
                tmp = ''
                for node in nodes:
                    if re.search('<h3>.*</h3>', node.get()) is not None:
                        # 如果是<h3>，那么说明该节点是一个小标题
                        