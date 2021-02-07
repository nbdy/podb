from uuid import uuid4
import shelve
from datetime import datetime


FMT_TIMESTAMP = "%Y.%m.%d %H:%M:%S"


class DBEntry(object):
    def __init__(self, **kwargs):
        self.uuid = str(uuid4())
        self.created = datetime.now()
        self.last_modified = self.created
        self.__dict__.update(kwargs)


class DB(object):
    def __init__(self, name: str):
        self.db = shelve.open(name)

    @staticmethod
    def has_keys(d: dict, keys: list[str]) -> bool:
        for k in keys:
            if k not in d.keys():
                return False
        return True

    @staticmethod
    def k_v_match(d: dict, c: dict) -> bool:
        if not DB.has_keys(d, list(c.keys())):
            return False
        for k in c.keys():
            if d[k] != c[k]:
                return False
        return True

    @staticmethod
    def update_values(o: DBEntry, n: DBEntry) -> DBEntry:
        for k, v in n.__dict__.items():
            o.__dict__[k] = v
        return o

    def insert(self, o: DBEntry, upsert=False) -> bool:
        if o.uuid in self.db.keys() and not upsert:
            return False
        self.db[o.uuid] = o
        self.db.sync()
        return True

    def insert_many(self, lst: list[DBEntry], upsert=False) -> bool:
        for e in lst:
            if not self.insert(e, upsert):
                return False
        return True

    def update(self, o: DBEntry, upsert=False) -> bool:
        if o.uuid not in self.db.keys() and not upsert:
            return False
        old = self.db[o.uuid]
        o.last_modified = datetime.now()
        o = self.update_values(old, o)
        self.db[o.uuid] = o
        self.db.sync()
        return True

    def update_many(self, lst: list[DBEntry], upsert=False) -> bool:
        for e in lst:
            if not self.update(e, upsert):
                return False
        return True

    def upsert(self, o: DBEntry) -> None:
        if o.uuid in self.db.keys():
            o.last_modified = datetime.now()
            self.db[o.uuid].__dict__.update(o.__dict__)
        else:
            self.db[o.uuid] = o
        self.db.sync()

    def upsert_many(self, lst: list[DBEntry]) -> None:
        for e in lst:
            self.upsert(e)

    def match(self, fltr, n=0) -> list:
        r = []
        for v in self.db.values():
            if len(r) >= n > 0:
                break
            if fltr(v.__dict__):
                r.append(v)
        return r

    def find(self, query: dict, n=0) -> list:
        def f(v: dict):
            return self.k_v_match(v, query)
        return self.match(f, n)

    def find_by_uuid(self, uuid):
        return self.db[uuid]

    def find_one(self, query: dict):
        r = self.find(query, 1)
        if len(r) > 0:
            return r[0]
        return None

    def find_after(self, timestamp: datetime, key="created", n=0) -> list:
        def f(v: dict):
            return v[key] > timestamp
        return self.match(f, n)

    def find_before(self, timestamp: datetime, key="created", n=0) -> list:
        def f(v: dict):
            return v[key] < timestamp
        return self.match(f, n)

    def size(self):
        return len(self.db.keys())

    def contains(self, query: dict):
        return self.find_one(query) is not None
