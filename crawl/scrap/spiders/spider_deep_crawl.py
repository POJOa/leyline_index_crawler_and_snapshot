#-*- coding: UTF-8 -*-
import scrapy
import re
import requests
from scrapy.spiders import Spider
import simplejson as json
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

        '''
        for line in json.load(open("res4.json")):
            self.start_urls.append(line['link'])
            self.allowed_domains.append(get_tld(line['link']))

        
        for dom in self.start_urls:
            self.allowed_domains.append(get_tld(dom))
        '''
        '''
        existed = []
        for line in json.load(open("res6.json")):
            if get_tld(line['link']) not in existed:
                existed.append(get_tld(line['link']))
        '''
        client = MongoClient('mongodb://localhost:27017/')
        db = client.src_index
        collection = db.NewSites


        existed = []
        for line in json.load(open("deep_io_me_cc_im.json")):
            if get_tld(line['link']) not in existed:
                existed.append(get_tld(line['link']))

        for e in collection.find({"groups":"个站","$or":[{"url":{"$regex":"\\.me"}},{"url":{"$regex":"\\.im"}},{"url":{"$regex":"\\.cc"}},{"url":{"$regex":"\\.io"}}]}):
            dom = get_tld(e['url'])
            if(dom not in existed):
                print(dom)
                self.start_urls.append(e['url'])
                self.allowed_domains.append(get_tld(e['url']))

        '''
        self.start_urls.append('http://touko.moe/')
        self.allowed_domains.append('touko.moe')
        '''
        print(len(self.start_urls))

    def parse(self, response):
        if('image'  in response.url or
                'git'  in response.url or
                'login'  in response.url or
                'admin'  in response.url or
                'reg'  in response.url  or
                'jpg'  in response.url or
                'ons.me' in response.url or
                'code.atr.me' in response.url or
                'thoj' in response.url or
               'gif'  in response.url or
                'png'  in response.url or
                'fossil'  in response.url or
                'comment'  in response.url or
                'shop'  in response.url or
                'mall'  in response.url or
                'reply'  in response.url or
                'dmg'  in response.url):
            return
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
                    "contains(name(), 'style') or"
                    "contains(name(), 'aside') or"
                    "contains(name(), 'script')"

                "])]").extract()).strip()

        if(len(response.url.split('/'))>4 and
                   'tag' not in response.url and
                   'archive' not in response.url and
                   'categor' not in response.url and
                   'feed' not in response.url and
                   'comment' not in response.url and
                   'author' not in response.url and
                   'image' not in response.url and
                   'git' not in response.url and
                   'login' not in response.url and
                   'admin' not in response.url and
                   'reg' not in response.url and
                   'page' not in response.url and
                   '2006' not in response.url and
                   '2007' not in response.url and
                   '2008' not in response.url and
                   '2009' not in response.url and
                   '2010' not in response.url and
                   '2011' not in response.url and
                   '2012' not in response.url and
                   '2013' not in response.url and
                   '2014' not in response.url and
                   '2015' not in response.url and
                   '2016' not in response.url and
                   'fossil' not in response.url and
                   'comment' not in response.url and
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
            if (url_txt is not None and
               'image' not in url_txt and
                            'git' not in url_txt and
                            'login' not in url_txt and
                            'admin' not in url_txt and
                            'reg' not in url_txt and
                            'jpg' not in url_txt and
                            'gif' not in url_txt and
                            'png' not in url_txt and
                            'fossil' not in url_txt and
                            'comment' not in url_txt and
                            'shop' not in url_txt and
                            'mall' not in url_txt and
                            'reply' not in url_txt and
                            'dmg' not in url_txt):
                yield scrapy.Request(response.urljoin(url_txt), callback=self.parse)

