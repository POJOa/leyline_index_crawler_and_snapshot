from multiprocessing import Pool
from task import tsk



def main():
    p = Pool(100)
    for line in open("dict4.txt"):
        p.apply_async(tsk,args=(line,))
    p.close()
    p.join()

if __name__=='__main__':
    main()
