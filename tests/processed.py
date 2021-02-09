from multiprocessing import Pool, cpu_count
from podb import DB, DBEntry
from random import choices, randint, uniform, choice
from datetime import datetime
from string import ascii_lowercase


db = DB("processed")


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


def insert_random_entry(x):
    db.insert(HugeDBItem.random())


if __name__ == '__main__':
    with Pool() as pool:
        pool.map(insert_random_entry, range(500000))
        pool.close()

    db.drop()
    print("cpus: {0} ; items: {1}".format(cpu_count(), 500000))
    e = cpu_count() * 500000
    a = db.size()
    print("expected: {0} ; actual: {1}".format(e, a))
    assert e == a
