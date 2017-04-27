import requests
import re
import datetime
import os, time

from memory_profiler import profile
from selenium import webdriver
from multiprocessing import Pool
from pymongo import MongoClient




'reachableAndInChinese'
def checkQualified(url):
    zhPattern = re.compile(u"[\u4e00-\u9fa5]+")
    try:
        r = requests.get(url,timeout=1)
        r.encoding = "utf-8"
        content = r.text
        return zhPattern.search(content) is not None
    except Exception as e:
        'print(url + " not available...")'
        return None

def process(url):
    browser = webdriver.Chrome("./chromedriver")
    browser.set_window_size(1280, 1024)
    try:
        browser.get(url)
        thumb = browser.get_screenshot_as_base64()
        title = browser.title
        try:
            description = browser.find_element_by_xpath("//meta[translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='description']").get_attribute("content")
        except:
            description = None
        try:
            author = browser.find_element_by_xpath("//meta[translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='author']").get_attribute("content")
        except:
            author = None
        try:
            keywords = browser.find_element_by_xpath("//meta[translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='keywords']").get_attribute("content")
        except:
            keywords = None
    except Exception as e:
        print(url + " - " + str(e))
    finally:
        entity = {
            "url": url,
            "thumb":thumb,
            "images":[],
            "title":title,
            "meta":{
                "description": description,
                "author": author,
                "keywords": keywords
            },
            "createdAt":datetime.datetime.utcnow()
        }

        client = MongoClient('mongodb://localhost:27017/')
        db = client.src_index
        collection = db.Sites
        entity_id = str(collection.insert_one(entity).inserted_id)
        print(url+" "+entity_id)
        browser.close()

def tsk(line):
    line = line.replace('\n', '')

    print(line)

    url = "http://" + line + ".moe"
    qualified = checkQualified(url)

    if qualified is None:
        url = "http://www." + line + ".moe"
        qualified = checkQualified(url)

    if qualified is True:
       process(url)
