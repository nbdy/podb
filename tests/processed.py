from multiprocessing import Pool, cpu_count
from podb import DB
from tests import HugeDBItem

db = DB("processed")


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
