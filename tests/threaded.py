from runnable import Runnable
import unittest
from podb import DBEntry, DB
from random import choices, randint, uniform, choice
from datetime import datetime
from string import ascii_lowercase
from time import time
from tqdm import tqdm


db = DB("threaded")


class HugeDBItem(DBEntry):
    def __init__(self, name: str, age: int, height: float, weight: float, color: str, birth_date: datetime):
        DBEntry.__init__(self)
        self.name = name
        self.age = age
        self.height = height
        self.weight = weight
        self.color = color
        self.birth_date = birth_date

    @staticmethod
    def random():
        return HugeDBItem(
            ''.join(choices(ascii_lowercase, k=30)),
            randint(1, 99),
            uniform(1.0, 250.0),
            uniform(1.0, 600.0),
            choice(["black", "white", "brown", "really?"]),
            datetime.now()
        )


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
