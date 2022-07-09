import unittest
from podb import DB, DBEntry
from os.path import isfile


class Person(DBEntry):
    def __init__(self, name: str):
        DBEntry.__init__(self)
        self.name = name


class DBTests(unittest.TestCase):
    def test_insert(self):
        db = DB("test")
        self.assertTrue(db.insert(Person("Jeff")))
        self.assertTrue(db.insert(DBEntry(**{"name": "Jeffrey"})))
        self.assertEqual(len(db.find_all_with_key("name")), 2)
        self.assertTrue(db.delete({"name": "Jeff"}))
        self.assertEqual(len(db.find_all_with_key("name")), 1)
        self.assertTrue(db.delete({"name": "Jeffrey"}))

    def test_insert_many(self):
        db = DB("test")
        self.assertTrue(db.insert_many([Person("Olaf"), Person("Walter")]))
        self.assertEqual(len(db.find_all_with_key("name")), 2)
        self.assertTrue(db.delete({"name": "Olaf"}))
        self.assertEqual(len(db.find_all_with_key("name")), 1)
        self.assertTrue(db.delete({"name": "Walter"}))

    def test_get_columns(self):
        db = DB("test")
        self.assertTrue(db.insert(Person("Richard")))
        self.assertTrue("name" in db.get_columns())
        self.assertTrue(db.drop())

    def test_contains(self):
        db = DB("test")
        self.assertTrue(db.insert(Person("Simon")))
        self.assertTrue(db.contains({"name": "Simon"}))
        self.assertTrue(db.drop())

    def test_find_startswith(self):
        db = DB("test")
        self.assertTrue(db.insert(Person("Helena")))
        self.assertEqual(len(db.find_startswith("name", "Hel")), 1)
        self.assertTrue(db.drop())

    def test_find_endswith(self):
        db = DB("test")
        self.assertTrue(db.insert(Person("Dilan")))
        self.assertEqual(len(db.find_endswith("name", "lan")), 1)
        self.assertTrue(db.drop())

    def test_find_contains(self):
        db = DB("test")
        self.assertTrue(db.insert(Person("Lincoln")))
        self.assertEqual(len(db.find_contains("name", "ncol")), 1)
        self.assertTrue(db.drop())

    def test_find_before(self):
        db = DB("test")
        self.assertTrue(db.insert(Person("John")))
        self.assertEqual(len(db.find_contains("name", "Jo")), 1)
        self.assertTrue(db.drop())
        self.assertIsNone(db.find_one({"name": "John"}))

    def test_find_by_uuid(self):
        db = DB("test")
        entry = Person("Johnathan")
        self.assertTrue(db.insert(entry))
        self.assertEqual(db.find_by_uuid(entry.uuid).name, entry.name)
        self.assertTrue(db.drop())
