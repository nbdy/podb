from podb import DB, DBEntry

from random import choice, randint, uniform
from string import printable
import unittest
import pickle
from copy import copy


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
        to = TestObject.random()
        b = tbl.size()
        tbl.insert(to)
        a = tbl.size()
        self.assertGreater(a, b, "DB entry count increased")

    def test_get_kv(self):
        to = TestObject.random()
        tbl.insert(to)
        ti = tbl.get_by("name", to.name)
        self.assertIsNotNone(ti, "get_kv returned not None")
        self.assertEqual(ti.uuid, to.uuid, "Inserted and retrieved object uuids are the same")

    def test_get_by_object(self):
        to = TestObject.random()
        tp = pickle.dumps(to)
        tbl.insert(to)
        ti = tbl.get_by("object", tp)
        self.assertIsNotNone(ti, "get_kv by object is not None")
        tip = pickle.dumps(ti)
        self.assertEqual(tp, tip, "inserted and retrieved pickle representations are equal")

    def test_get_uuid(self):
        to = TestObject.random()
        tbl.insert(to)
        ti = tbl.get_by_uuid(to.uuid)
        self.assertIsNotNone(ti, "get_uuid returned not None")
        self.assertEqual(to.uuid, ti.uuid, "Inserted and retrieved object uuids are the same")

    def test_update(self):
        to = TestObject.random()
        tbl.insert(to), "database insert"
        toageb = int(to.age)
        tosizeb = float(to.size)
        to.age *= 2
        to.size *= 2
        self.assertNotEqual(toageb, to.age, "doubled the age")
        self.assertNotEqual(tosizeb, to.size, "doubled the size")
        tbl.update(to)
        ti = tbl.get_by_uuid(to.uuid)
        self.assertIsNotNone(ti, "get_uuid returned not None")
        self.assertGreater(ti.size, tosizeb, "greater than original objects age")
        self.assertGreater(ti.age, toageb, "greater than original objects age")


if __name__ == '__main__':
    db = DB("test")
    tbl = db.t("testTbl")
    unittest.main()
