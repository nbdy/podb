from podb import DB, DBEntry

from random import choice, randint, uniform
from string import printable
from threading import Thread
from multiprocessing import Queue
import unittest
from time import time, sleep
from datetime import datetime
from copy import deepcopy

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
        b = db.size()
        db.insert(to)
        a = db.size()
        self.assertGreater(a, b, "DB entry count did not increase")

    def test_get_by(self):
        print("test_get_by")
        to = TestObject.random()
        db.insert(to)
        ti = db.find_one({"name": to.name})
        self.assertIsNotNone(ti, "get_kv returned None")
        self.assertEqual(ti.uuid, to.uuid, "Inserted and retrieved object uuids are not the same")

    def test_get_uuid(self):
        print("test_get_uuid")
        to = TestObject.random()
        db.insert(to)
        ti = db.find_one({"uuid": to.uuid})
        self.assertIsNotNone(ti, "get_uuid returned None")
        self.assertEqual(to.uuid, ti.uuid, "Inserted and retrieved object uuids are not the same")

    def test_update(self):
        print("test_update")
        t0 = TestObject.random()
        db.insert(t0)
        t1 = deepcopy(t0)
        t0.age *= 2
        t0.size *= 2
        print(t1.age, t1.size)
        print(t0.age, t0.size)
        self.assertGreater(t0.age, t1.age, "age is not greater than before")
        self.assertGreater(t0.size, t1.size, "size is not greater than before")
        self.assertTrue(db.update(t0), "update failed")
        del t0
        t0 = db.find_by_uuid(t1.uuid)
        self.assertIsNotNone(t0, "get_uuid returned None")
        self.assertGreater(t0.size, t1.size, "not greater than original objects age")
        self.assertGreater(t0.age, t1.age, "not greater than original objects age")

    def test_timings(self):
        print("test_timings")
        avg_queue = Queue()

        def f(q: Queue, n=200):
            avg = 0
            for _ in range(n):
                start = time()
                db.insert(TestObject.random())
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
        db.insert_many([t0, t1])
        r = db.find_after(now)
        self.assertIsNotNone(r, "get_after returned something")


if __name__ == '__main__':
    unittest.main()
