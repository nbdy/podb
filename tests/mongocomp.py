from pymongo import MongoClient
from . import HugeDBItem
from tqdm import tqdm
import unittest


c = MongoClient()
db = c["mongodbinsert"]
col = db["bigboi"]


class MongoDBInserter(unittest.TestCase):
    def test_mongo_insert(self):
        for _ in tqdm(range(1000000)):
            col.insert_one(HugeDBItem.random().__dict__)


if __name__ == '__main__':
    unittest.main()
