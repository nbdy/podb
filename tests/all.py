from podb import DB
from threading import Thread
from multiprocessing import Queue
import unittest
from time import time, sleep
from datetime import datetime
from copy import deepcopy
from tests import TestObject

db = DB("test")


class DBTestMethods(unittest.TestCase):
    def test_insert(self):
        print("test_insert")
        to = TestObject.random()
        b = db.size()
        db.insert(to)
        a = db.size()
        self.assertGreater(a, b, "DB entry count did not increase")

    def test_find(self):
        print("test_find")
        to = TestObject.random()
        self.assertTrue(db.insert(to), "insert was not successful")
        self.assertGreater(db.size(), 0, "database count is still 0")
        ti = db.find_one({"name": to.name})
        self.assertIsNotNone(ti, "find_one returned None")
        self.assertEqual(ti.uuid, to.uuid, "Inserted and retrieved object uuids are not the same")

    def test_find_by_uuid(self):
        print("test_find_by_uuid")
        to = TestObject.random()
        db.insert(to)
        ti = db.find_by_uuid(to.uuid)
        self.assertIsNotNone(ti, "find_by_uuid returned None")
        self.assertEqual(to.uuid, ti.uuid, "Inserted and retrieved object uuids are not the same")

    def test_update(self):
        print("test_update")
        t0 = TestObject.random()
        db.insert(t0)
        t1 = deepcopy(t0)
        t0.age *= 2
        t0.size *= 2
        self.assertGreater(t0.age, t1.age, "age is not greater than before")
        self.assertGreater(t0.size, t1.size, "size is not greater than before")
        self.assertTrue(db.update(t0), "update failed")
        del t0
        t0 = db.find_by_uuid(t1.uuid)
        self.assertIsNotNone(t0, "find_by_uuid returned None")
        self.assertGreater(t0.size, t1.size, "not greater than original objects age")
        self.assertGreater(t0.age, t1.age, "not greater than original objects age")

    def test_timings(self):
        db.drop()
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
            avg_result = avg_queue.get()
            self.assertLess(avg_result, 0.2, "processing time is lesser than 0.2 seconds")
        self.assertEqual(db.size(), 800, "db has size of {0} not 800".format(db.size()))

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
    db.drop()
    unittest.main()
