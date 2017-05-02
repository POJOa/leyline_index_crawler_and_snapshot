#-*- coding: UTF-8 -*-
# encoding=utf8


import requests
import re
import datetime
import os, time
from tld import get_tld
from selenium import webdriver
from multiprocessing import Pool
from pymongo import MongoClient
from pymongo import MongoClient
from io import StringIO
import simplejson as json
import base64
from bson import Binary, Code
from bson.json_util import dumps
import requests
from multiprocessing import Pool
from tld import get_tld

from selenium.webdriver.support.ui import WebDriverWait


def uploadImage(e):
    try:
        r = requests.post('http://x.mouto.org/wb/x.php?up', e)
        resJson = r.json()
        if resJson['pid'] is not None:
            return resJson['pid']
        else:
            return None
    except Exception as e:
        return None




def process(line):
    url=line['link']

    client = MongoClient('mongodb://localhost:27017/')
    db = client.src_index
    collection = db.NewSites

    existed = len(list(collection.find({"url": {"$regex": get_tld(url)}}))) >0

    if existed:
       return

    browser = webdriver.Chrome("./chromedriver")
    browser.set_window_size(1280, 1024)
    browser.set_page_load_timeout(10)
    try:
        browser.get(url)
    except Exception as e:
        browser.execute_script('window.stop()')
        print(url + " - " + str(e))
    finally:
        print(url + " - taking snapshot")
        thumb = None

        title = browser.title
        try:
            description = browser.find_element_by_xpath(
                "//meta[translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='description']").get_attribute(
                "content")
        except:
            description = None
        try:
            author = browser.find_element_by_xpath(
                "//meta[translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='author']").get_attribute(
                "content")
        except:
            author = None
        try:
            keywords = browser.find_element_by_xpath(
                "//meta[translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='keywords']").get_attribute(
                "content")
        except:
            keywords = None

        try:
            print("uploading thumb of " + url)
            thumb = None
            retry = 0
            image = browser.get_screenshot_as_png()
        except Exception as e:
            print(url + " - " + str(e))

        browser.close()

        while thumb is None and retry<10:
            retry += 1
            thumb = uploadImage(image)
        if thumb is None:
            print(url + " snapshot upload failed")
            thumb = image
        else :
            print(url + " snapshot upload okay")




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
            "createdAt":datetime.datetime.utcnow(),
            "raw":{
                "text":line["text"],
                "src":line["src"]
            }
        }

        entity_id = str(collection.insert_one(entity).inserted_id)
        print(url+" "+entity_id)


# noinspection PyArgumentList
def main():
    p = Pool(5)
    with open("res9.json", encoding='utf-8') as data_file:
        arr = json.load(data_file)
    for line in arr:
        p.apply_async(process, args=(line,))
    p.close()
    p.join()

if __name__ == '__main__':
    main()
