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

        # get GEM
        if 'gem' not in sources: # 如果没有"gem"部分就跳吧
            yield None
        elif 'gem' in sources:
            gem = response.xpath('//section[@data-src="gem"]')
            item['word'] = gem.xpath('./h2/text()').get()
            nodes = gem.xpath('./child::*')

            # Branch 1: if <h3> is in nodes
            hasBranches = False # 整个词条如果有无分支用这个布尔值来界定，默认值为False
            keys = list() # 存放字典的键
            obj = dict() # 盛放分支

            # Branch 2: if only meaning
            meaning = '' # 如果只有单条意思，就起用这个字段

            # 两条支线
            for node in nodes:
                nodeGet = node.get()
                if re.search('<h3>.*</h3>', nodeGet):
                    # 如果是<h3>，那么说明该节点是一个小标题。整个词条都是小标题+分支的形式。
                    # 启用分支1
                    hasBranches = True
                    obj[node.xpath('./text()').get()] = '' # 键值对中的值是字符串
                    keys.append(node.xpath('./text()').get())
                elif re.search('<div class="runseg">.*</div>', nodeGet):
                    if hasBranches:
                        obj[keys[-1]] += self.dropTags(nodeGet) 
                    else:
                        # 如果只有一条意思，启用分支2
                        meaning += self.dropTags(nodeGet) 
                elif re.search('<div class="ds-single" .*>.*</div>', nodeGet):
                    # 几乎是必经之路
                    obj['relations'] = node.xpath('./a/@href').getall()
                else:
                    pass
            
            if hasBranches:
                item['meanings'] = obj
            else:
                item['meanings'] = meaning

            yield item