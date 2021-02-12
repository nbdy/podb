from runnable import Runnable
import unittest
from podb import DB
from time import time
from tqdm import tqdm
from . import HugeDBItem


db = DB("threaded")


class ThreadedInserter(Runnable):
    def work(self):
        for _ in range(1000):
            db.insert(HugeDBItem.random())
        self.do_run = False


class ThreadedTest(unittest.TestCase):
    def test_threaded(self):
        print("test threaded")
        db.drop()
        lst = []
        for _ in range(128):
            lst.append(ThreadedInserter())
        s = time()
        for _ in lst:
            _.start()
        print("created and started inserters")
        for _ in tqdm(lst, total=len(lst)):
            _.join()
        e = time()
        r = e - s
        expected = 128 * 1000
        print("start:", s)
        print("end:", e)
        print("diff:", r)
        print("count:", db.size(), "expected:", expected)
        print("threads: {0}; count: 1000".format(128))
        self.assertEqual(expected, db.size())


if __name__ == '__main__':
    unittest.main()
