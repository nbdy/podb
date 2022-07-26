from uuid import uuid4
import shelve
from datetime import datetime
from typing import List
from filelock import FileLock
from random import randint


FMT_TIMESTAMP = "%Y.%m.%d %H:%M:%S"


class DBEntry(object):
    def __init__(self, **kwargs):
        self.uuid = str(uuid4())
        self.created = datetime.now()
        self.last_modified = self.created
        for k, v in kwargs.items():
            self.__dict__[k] = v


class DB(object):
    def __init__(self, path: str):
        self.database = shelve.open(path)
        self._lock = FileLock(path + ".lock")

    @staticmethod
    def has_keys(d: dict, keys: List[str]) -> bool:
        for k in keys:
            if k not in d.keys():
                return False
        return True

    def k_v_match(self, d: dict, c: dict) -> bool:
        if not self.has_keys(d, list(c.keys())):
            return False
        for k in c.keys():
            if d[k] != c[k]:
                return False
        return True

    def _insert(self, o, upsert=False) -> bool:
        if o.uuid in self.database.keys() and not upsert:
            return False
        self.database[o.uuid] = o
        return True

    def insert(self, o: DBEntry, upsert=False) -> bool:
        return self._insert(o, upsert)

    def insert_many(self, lst: list, upsert=False) -> bool:
        return all([self._insert(item, upsert) for item in lst])

    def _update(self, o, upsert=False) -> bool:
        if o.uuid not in self.database.keys() and not upsert:
            return False
        old = self.database[o.uuid]
        for key, value in o.__dict__.items():
            old.__dict__[key] = value
        old.last_modified = datetime.now()
        self.database[o.uuid] = old
        return True

    def update(self, o, upsert=False) -> bool:
        with self._lock:
            return self._update(o, upsert)

    def update_many(self, lst: list, upsert=False) -> List[bool]:
        with self._lock:
            return [self._update(item, upsert) for item in lst]

    def _upsert(self, o) -> None:
        if o.uuid in self.database.keys():
            o.last_modified = datetime.now()
            self.database[o.uuid].__dict__.update(o.__dict__)
        else:
            self.database[o.uuid] = o

    def upsert(self, o) -> None:
        with self._lock:
            self._upsert(o)

    def upsert_many(self, lst: list) -> None:
        with self._lock:
            [self._upsert(item) for item in lst]

    def match(self, fltr, n=0) -> list:
        r = []
        with self._lock:
            for v in self.database.values():
                if 0 < n < len(r):
                    break
                if fltr(v.__dict__):
                    r.append(v)
        return r

    def find(self, query: dict, n=0) -> list:
        return self.match(lambda v: self.k_v_match(v, query), n)

    def find_by_uuid(self, uuid):
        return self.database.get(uuid)

    def find_one(self, query: dict):
        r = self.find(query, 1)
        if len(r) > 0:
            return r[0]
        return None

    def find_after(self, timestamp: datetime, key="created", n=0) -> list:
        return self.match(lambda v: v[key] > timestamp, n)

    def find_before(self, timestamp: datetime, key="created", n=0) -> list:
        return self.match(lambda v: v[key] < timestamp, n)

    def find_contains(self, key: str, value: str, n=0):
        return self.match(lambda v: value in v[key], n)

    def find_startswith(self, key: str, value: str, n=0):
        return self.match(lambda v: v[key].startswith(value), n)

    def find_endswith(self, key: str, value: str, n=0):
        return self.match(lambda v: v[key].endswith(value), n)

    def find_all_with_key(self, key: str, n=0):
        return self.match(lambda v: key in v.keys(), n)

    def size(self):
        return len(self.database.keys())

    def contains(self, query: dict):
        return self.find_one(query) is not None

    def get_columns(self) -> list:
        r = []
        with self._lock:
            for item in self.database.values():
                r += list(set(item.__dict__.keys()))
        return list(set(r))

    def drop(self):
        with self._lock:
            self.database.clear()
        return self.size() == 0

    def delete(self, fltr: dict):
        r = 0
        for i in self.find(fltr):
            with self._lock:
                del self.database[i.uuid]
            r += 1
        return r > 0

    def delete_by_uuid(self, uuid: str):
        if uuid in self.database.keys():
            with self._lock:
                del self.database[uuid]
            return True
        return False

    def delete_before(self, before: datetime, key="created") -> int:
        r = 0
        for i in self.find_after(before, key):
            with self._lock:
                self.database.pop(i.uuid)
            r += 1
        return r

    def get_all(self):
        return self.database.items()

    def get_random(self):
        return self.database[
            list(self.database.keys())[
                randint(0, len(self.database.keys()) - 1)
            ]
        ]

    def get_random_list(self, n: int):
        return [self.get_random() for _ in range(n)]
