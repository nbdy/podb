import unittest
from podb import DB
from tqdm import tqdm
from . import HugeDBItem

db = DB("huge")


class HugeDBTest(unittest.TestCase):
    def test_huge_insert(self):
        for _ in tqdm(range(1000000)):
            db.insert(HugeDBItem.random())


if __name__ == '__main__':
    unittest.main()
