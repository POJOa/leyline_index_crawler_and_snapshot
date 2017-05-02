#-*- coding: UTF-8 -*-
import scrapy
import re
import requests
from scrapy.spiders import Spider

from scrapy import Selector
from scrapy.item import Item, Field
from tld import get_tld
from pymongo import MongoClient


class scrap(Spider):
    name = 'src_spider_pojo'

    class Site(Item):
        text = Field()
        link = Field()
        src = Field()

    def __init__(self, category=None, *args, **kwargs):

        super(scrap, self).__init__(*args, **kwargs)
        self.res = []
        self.items = []
        self.bannedList = []
        self.banned_url_keywords = []

        for line in open("./bannedList.txt"):
            self.bannedList.append(line.replace('\n',''))

        for line in open("./bannedUrlKeywords.txt"):
            self.banned_url_keywords.append(line.replace('\n',''))

        self.crawled_pages = {}
        self.first_kiss_domains = {}

        self.maximumPagesPerSite = 20  # maximum pages each site

        client = MongoClient('mongodb://localhost:27017/')
        db = client.src_index
        collection = db.NewSites

        self.allowed_domains = []
        self.start_urls = []

        for e in collection.find():
            self.start_urls.append(e['url'])
            self.allowed_domains.append(get_tld(e['url']))

            '''
            if datetime.datetime.fromtimestamp(1493424995) < e['createdAt']:
                self.start_urls.append(e['url'])
                self.allowed_domains.append(get_tld(e['url']))
                    for dom in self.start_urls:
            self.allowed_domains.append(get_tld(dom))
    
        '''


    'reachableAndInChinese'
    def check_reachable_and_in_chinese(self,url,wait):
        zhPattern = re.compile(u"[\u4e00-\u9fa5]+")
        try:
            r = requests.get(url, timeout=wait)
            r.encoding = "utf-8"
            content = r.text
            return zhPattern.search(content) is not None
        except Exception as e:
            'print(url + " not available...")'
            return None


    def get_valid(self,url):
        try:
            get_tld(url)
        except:
            print(url + "is illegal")
            return None

        'qualified = self.check_reachable_and_in_chinese(url)'
        'print("trying " + url)'
        qualified = None
        if qualified is None:
            url = "http://" + get_tld(url)
            qualified = self.check_reachable_and_in_chinese(url , 3)
            print("trying " + url)

        if qualified is None:
            url = "http://www." + get_tld(url)
            qualified = self.check_reachable_and_in_chinese(url , 1)
            print("trying " + url)

        if qualified is None:
            url = "http://blog." + get_tld(url)
            qualified = self.check_reachable_and_in_chinese(url , 1)
            print("trying " + url)

        if qualified is True:
            print(url + " is reachable")
            return url.lower()

        else:
            return None


    def check_banned_domain(self,domain,url):
        domain_not_banned = domain not in self.bannedList
        if not domain_not_banned:
            print(domain + ' is banned in list')

        domain_not_banned_by_keyword_rules = domain_not_banned
        for line in self.banned_url_keywords:
            if domain_not_banned_by_keyword_rules:
                domain_not_banned_by_keyword_rules = line not in url
        if not domain_not_banned_by_keyword_rules:
            print(domain + ' is banned by keyword rules')

        return domain_not_banned_by_keyword_rules

    def check_valid_domain(self,url):
        if url is  None:
            return False
        url = url.lower()
        domain = get_tld(url)
        if domain in self.res:
            print(domain + ' is already presented in result')
            return False

        domain_not_banned = self.check_banned_domain(domain,url)
        if not domain_not_banned:
            return False

        client = MongoClient('mongodb://localhost:27017/')
        db = client.src_index
        collection = db.NewSites

        not_existed = len(list(collection.find({"url": {"$regex":domain}}))) < 1

        if not not_existed:
            print(domain + ' already existed in DB')

        return domain_not_banned and not_existed

    def check_valid(self,url):


        valid=self.check_valid_domain(url)
        if(valid) :
            res = self.get_valid(url)
            if res is None:
                print(url + ' is not reachable')
        else :
            res = None
        return res


    def check_if_reachable(self,url,pattern):
        anti_fake_200 = ['404','gandi','error','找不到','页面不','删除']

        try:
            print('trying ' + pattern +' as first contact url for ' + url)
            r = requests.get(url + pattern, timeout=2)
            r.raise_for_status()
            for damned_word in anti_fake_200:
                if damned_word in r.text:
                    return False
            return True
        except:
            return False

    def get_first_kiss_url(self,url):
        oldUrl = url
        url = self.get_valid(url)

        if url is not None:
            print('first contacting ' + url)
            pattern = None
            if self.check_if_reachable(url,'/links'):
                pattern = '/links'
            if self.check_if_reachable(url, '/friends'):
                pattern = '/friends'
            if self.check_if_reachable(url, '/about'):
                pattern = '/about'

            if pattern is not None:
                return url + pattern

        print('first contact url for ' + oldUrl + ' ALL FAILED')
        return None


    def first_kiss(self,domain,url):

        if domain in self.allowed_domains and domain not in self.first_kiss_domains:
            print('first contact with '+url + ' of ' + domain)

            first_kiss_url = self.get_first_kiss_url(url)

            self.first_kiss_domains[domain] = -1

            if first_kiss_url is not None:
                print(first_kiss_url + ' is selected as first contact url')
                self.first_kiss_domains[domain] = first_kiss_url

                return first_kiss_url
        return None


    def parse(self, response):
        domain = get_tld(response.url)
        if len(response.url.replace("http://","").split('/')) > 4:
            return
        if domain in self.first_kiss_domains:
            if self.first_kiss_domains[domain] != response.url and self.first_kiss_domains[domain] != -1:
                print(response.url + " has a first-contacted page and will be ignored")
                return
            else:
                if self.first_kiss_domains[domain] == response.url:
                    print("HITTING first-contact page : " + response.url)

        if domain in self.allowed_domains:
            if domain in self.crawled_pages:
                # If enough page visited in this domain, return
                if self.crawled_pages[domain] > self.maximumPagesPerSite:
                    return
                self.crawled_pages[domain] += 1
                print(domain + ' was visited for ' + str(self.crawled_pages[domain]) + ' times')

        hxs = Selector(response)
        new_urls = hxs.xpath('//a')
        if len(new_urls)<4:
            return
        for url in new_urls:
            url_txt = url.xpath('@href').extract_first()


            if url_txt is None:
                continue

            if len(url_txt.split('/'))<2:
                print(url_txt + ' is homepage or empty')
                continue

            else:
                if not self.check_banned_domain(url_txt,url_txt):
                    print(url_txt + 'is banned')
                else:
                    print('processing ' + url_txt)


            valid_url = self.check_valid(response.urljoin(url_txt))

            if valid_url is not None:

                print(valid_url + ' seems yummy')
                if domain in self.crawled_pages and self.crawled_pages[domain] > 1:
                    self.crawled_pages[domain]-=1
                self.res.append(get_tld(url_txt))

                item = self.Site()
                item['text'] = url.xpath('text()').extract_first()
                item['link'] = valid_url.lower()
                item['src'] = response.url
                print(item)
                yield item

                if domain in self.allowed_domains:
                    if domain not in self.crawled_pages:

                        self.crawled_pages[domain] = 1
                        print(domain + ' has been visited for THE FIRST TIME')
                        first_kiss_url = self.first_kiss(domain, url_txt)
                        if first_kiss_url is not None:
                            yield scrapy.Request(first_kiss_url, callback=self.parse)
                            break
            try:
                'if crawling non-source site ,it  wont be allowed unless presented in allowed_domains array'
                if domain in self.allowed_domains:
                    yield scrapy.Request(response.urljoin(url_txt), callback=self.parse)
            except Exception as e:
                print(str(e))

