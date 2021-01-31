from podb import DB, DBEntry

from random import choice, randint, uniform
from string import printable
from threading import Thread
from multiprocessing import Queue
import unittest
import pickle
from time import time, sleep
from datetime import datetime

TBL = "test"
db = DB("test")


def generate_string(n=20, charset=printable):
    return ''.join(choice(charset) for _ in range(n))


class TestObject(DBEntry):
    def __init__(self, name: str, age: int, size: float):
        DBEntry.__init__(self)
        self.name = name
        self.age = age
        self.size = size

    @staticmethod
    def random():
        return TestObject(generate_string(), randint(0, 420), uniform(1.4, 2))


class DBTestMethods(unittest.TestCase):
    def test_insert(self):
        print("test_insert")
        to = TestObject.random()
        b = db.size(TBL)
        db.insert(TBL, to)
        a = db.size(TBL)
        self.assertGreater(a, b, "DB entry count increased")

    def test_get_by(self):
        print("test_get_by")
        to = TestObject.random()
        db.insert(TBL, to)
        ti = db.get_one_by(TBL, "name", to.name)
        self.assertIsNotNone(ti, "get_kv returned not None")
        self.assertEqual(ti.uuid, to.uuid, "Inserted and retrieved object uuids are the same")

    def test_get_by_object(self):
        print("test_get_by_object")
        to = TestObject.random()
        tp = pickle.dumps(to)
        db.insert(TBL, to)
        ti = db.get_one_by(TBL, "object", tp)
        self.assertIsNotNone(ti, "get_kv by object is not None")
        tip = pickle.dumps(ti)
        self.assertEqual(tp, tip, "inserted and retrieved pickle representations are equal")

    def test_get_uuid(self):
        print("test_get_uuid")
        to = TestObject.random()
        db.insert(TBL, to)
        ti = db.get_by_uuid(TBL, to.uuid)
        self.assertIsNotNone(ti, "get_uuid returned not None")
        self.assertEqual(to.uuid, ti.uuid, "Inserted and retrieved object uuids are the same")

    def test_update(self):
        print("test_update")
        to = TestObject.random()
        db.insert(TBL, to), "database insert"
        toageb = int(to.age)
        tosizeb = float(to.size)
        to.age *= 2
        to.size *= 2
        self.assertNotEqual(toageb, to.age, "doubled the age")
        self.assertNotEqual(tosizeb, to.size, "doubled the size")
        db.update(TBL, to)
        ti = db.get_by_uuid(TBL, to.uuid)
        self.assertIsNotNone(ti, "get_uuid returned not None")
        self.assertGreater(ti.size, tosizeb, "greater than original objects age")
        self.assertGreater(ti.age, toageb, "greater than original objects age")

    def test_timings(self):
        print("test_timings")
        avg_queue = Queue()

        def f(q: Queue, n=200):
            avg = 0
            for _ in range(n):
                start = time()
                db.insert(TBL, TestObject.random())
                stop = time()
                d = (stop - start)
                avg += d
            avg /= n
            q.put(avg)

        t = []
        for _ in range(4):
            t.append(Thread(target=f, args=[avg_queue]))
        for _ in t:
            _.start()
        for _ in t:
            _.join()
        while not avg_queue.empty():
            self.assertLess(avg_queue.get(), 0.2, "processing time is lesser than 0.2 seconds")

    def test_get_after(self):
        print("test_get_after")
        now = datetime.now()
        sleep(1)
        t0 = TestObject.random()
        t1 = TestObject.random()
        db.insert_many(TBL, [t0, t1])
        r = db.get_after(TBL, now)
        self.assertIsNotNone(r, "get_after returned something")


if __name__ == '__main__':
    unittest.main()
