from pymongo import MongoClient
from io import StringIO
import json
import base64
from bson import Binary, Code
from bson.json_util import dumps
import requests
from multiprocessing import Pool
from tld import get_tld
fail = []
success = []
client = MongoClient('mongodb://localhost:27017/')
db = client.src_index
collection = db.Sites
updatedCollection = db.NewSites
everything = collection.find()

def tsk(e):
    client = MongoClient('mongodb://localhost:27017/')
    db = client.src_index
    updatedCollection = db.NewSites
    thumb = base64.b64decode(e['thumb'])
    print("processing " + e['url'])
    try:
        r = requests.post('http://x.mouto.org/wb/x.php?up', thumb)
        resJson = r.json()
        if resJson['pid'] is not None:
            print("adding " + e['url'])
            e['thumb'] = resJson['pid']
            updatedCollection.insert(e)
            success.append(e['url'])
        else:
            print(resJson)
            fail.append(e['url'])
    except Exception as e:
        print(e['url']+' failing ' + str(e))
        fail.append(e['url'])


p = Pool(10)

for e in everything:
    if len(list(updatedCollection.find({"url":{"$regex":get_tld(e['url'])}})))<1:
        p.apply_async(tsk, args=(e,))
p.close()
p.join()

print("===============")
print(json.dumps(fail))