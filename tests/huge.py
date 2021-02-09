import unittest
from podb import DB, DBEntry
from datetime import datetime
from random import uniform, randint
from random import choices, choice
from string import ascii_lowercase
from tqdm import tqdm

db = DB("huge")


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


class HugeDBTest(unittest.TestCase):
    def test_huge_insert(self):
        for _ in tqdm(range(100000000)):
            db.insert(HugeDBItem.random())


if __name__ == '__main__':
    unittest.main()
