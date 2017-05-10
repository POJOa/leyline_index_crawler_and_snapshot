#-*- coding: UTF-8 -*-
import scrapy
import re
import requests
from scrapy.spiders import Spider

from scrapy import Selector
from scrapy.item import Item, Field
from tld import get_tld
from pymongo import MongoClient
import simplejson as json

class scrap(Spider):
    name = 'src_spider_pojo'

    class Detail(Item):
        text = Field()
        link = Field()
        title = Field()
        keywords = Field()


    def __init__(self, category=None, *args, **kwargs):

        super(scrap, self).__init__(*args, **kwargs)
        self.res = []
        self.items = []

        self.crawled_pages = {}
        self.first_kiss_domains = {}

        self.maximumPagesPerSite = 20  # maximum pages each site

        self.start_urls = []
        self.allowed_domains = []

        for line in json.load(open("res4.json")):
            self.start_urls.append(line['link'])
            self.allowed_domains.append(get_tld(line['link']))

        '''
        for dom in self.start_urls:
            self.allowed_domains.append(get_tld(dom))
        '''
        '''
        client = MongoClient('mongodb://localhost:27017/')
        db = client.src_index
        collection = db.Sites


        for e in collection.find():


            if datetime.datetime.fromtimestamp(1493424995) < e['createdAt']:
                start_urls.append(e['url'])
                allowed_domains.append(get_tld(e['url']))
        '''

    'reachableAndInChinese'



    def parse(self, response):

        hxs = Selector(response)
        expected_headline = hxs.xpath("//*[contains(@class, 'title')]//text()").extract_first()
        if expected_headline is None:
            expected_headline = ''.join(hxs.xpath("//h1//text()").extract()).strip()
        expected_keywords = ''.join(hxs.xpath("//h2//text()").extract()).strip()
        expected_keywords = expected_keywords.join(hxs.xpath("//h3//text()").extract()).strip()
        txt = ''.join(hxs.xpath("//*//text()[not("
                "ancestor-or-self::node()["
                    "contains(@class, 'title') or "
                    "contains(@id, 'header') or "
                    "contains(@id, 'nav') or "
                    "contains(@class, 'title') or "
                    "contains(@class, 'cat') or"
                    "contains(@class, 'search') or "
                    "contains(@class, 'header') or "
                    "contains(@class, 'nav') or "
                    "contains(name(), 'title') or "
                    "contains(name(), 'nav') or"
                    "contains(name(), 'header') or"
                    "contains(name(), 'aside') or"
                    "contains(name(), 'script')"

                "])]").extract()).strip()

        if(len(response.url.split('/'))>4 and
                   'tag' not in response.url and
                   'archive' not in response.url and
                   'category' not in response.url and
                   'author' not in response.url and
                   'page' not in response.url and
                   '2011' not in response.url and
                   '2012' not in response.url and
                   '2013' not in response.url and
                   '2014' not in response.url and
                   '2015' not in response.url and
                   '2016' not in response.url and
                   '2017' not in response.url

           ):
            item = self.Detail()
            item['text'] = txt.replace('\n','').replace('\r','').replace('\t','')
            item['link'] = response.url
            item['title'] = expected_headline
            item['keywords'] = expected_keywords
            print(response.url)
            yield item

        new_urls = hxs.xpath('//a')
        for url in new_urls:
            url_txt = url.xpath('@href').extract_first()
            if url_txt is not None:
                yield scrapy.Request(response.urljoin(url_txt), callback=self.parse)

