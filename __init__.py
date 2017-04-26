import requests
import re
import datetime
import os, time

from selenium import webdriver
from multiprocessing import Pool
from pymongo import MongoClient



client = MongoClient('mongodb://localhost:27017/')
db = client.src_index

zhPattern = re.compile(u"[\u4e00-\u9fa5]+")
p = Pool(5)

'reachableAndInChinese'
def checkQualified(url):
    try:
        r = requests.get(url)
        r.encoding = "utf-8"
        content = r.text
        return zhPattern.search(content) is not None
    except requests.ConnectionError:
        print(url + " not available...")
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
        collection = db.Sites
        entity_id = str(collection.insert_one(entity).inserted_id)
        print(url+" "+entity_id)
        browser.close()

def tsk(line):
    start = time.time()
    pid = str(os.getpid())
    line = line.replace('\n', '')

    print("checking " + line + " - pid " + pid)

    url = "http://" + line + ".moe"
    qualified = checkQualified(url)

    if qualified is None:
        url = "http://www." + line + ".moe"
        qualified = checkQualified(url)

    if qualified is True:
       process(url)

    duration = str(time.time() - start)
    print("pid " + pid + " runs for " + duration + " secs.")

def main():
    for line in open("dict.txt"):
        if(line.__len__()<4):
            continue
        p.apply_async(tsk,args=(line,))
    p.close()
    p.join()

if __name__=='__main__':
    main()