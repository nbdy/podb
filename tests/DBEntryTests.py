import unittest
from podb import DBEntry


class DBEntryTests(unittest.TestCase):
    def test_construction(self):
        entry = DBEntry()
        self.assertIsNotNone(entry.uuid)
        self.assertEqual(entry.created, entry.last_modified)

    def test_construction_kwargs(self):
        entry = DBEntry(**{"name": "Jeff"})
        self.assertEqual(entry.name, "Jeff")
