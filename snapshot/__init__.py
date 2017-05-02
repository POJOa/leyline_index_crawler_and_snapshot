from multiprocessing import Pool
from .task_for_spider import process
import simplejson as json


def main():
    p = Pool(5)
    for line in json.load(open("res9.json")):
        p.apply_async(process,args=(line,))
    p.close()
    p.join()

if __name__=='__main__':
    main()
