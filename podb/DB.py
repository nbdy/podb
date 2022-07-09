from uuid import uuid4
import shelve
from datetime import datetime
from typing import List
from filelock import FileLock


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
        self.db = shelve.open(path)
        self._lock = FileLock(path + ".lock")

    @staticmethod
    def has_keys(d: dict, keys: List[str]) -> bool:
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
    def update_values(o, n):
        for k, v in n.__dict__.items():
            o.__dict__[k] = v
        return o

    def _insert(self, o, upsert=False) -> bool:
        if o.uuid in self.db.keys() and not upsert:
            return False
        self.db[o.uuid] = o
        return True

    def insert(self, o: DBEntry, upsert=False) -> bool:
        return self._insert(o, upsert)

    def insert_many(self, lst: list, upsert=False) -> bool:
        r = []
        for e in lst:
            r.append(self._insert(e, upsert))
        return all(r)

    def _update(self, o, upsert=False) -> bool:
        if o.uuid not in self.db.keys() and not upsert:
            return False
        old = self.db[o.uuid]
        o.last_modified = datetime.now()
        o = self.update_values(old, o)
        self.db[o.uuid] = o

    def update(self, o, upsert=False) -> bool:
        with self._lock:
            self._update(o, upsert)
        return True

    def update_many(self, lst: list, upsert=False) -> bool:
        with self._lock:
            for e in lst:
                if not self._update(e, upsert):
                    return False
        return True

    def _upsert(self, o) -> None:
        if o.uuid in self.db.keys():
            o.last_modified = datetime.now()
            self.db[o.uuid].__dict__.update(o.__dict__)
        else:
            self.db[o.uuid] = o

    def upsert(self, o) -> None:
        with self._lock:
            self._upsert(o)

    def upsert_many(self, lst: list) -> None:
        with self._lock:
            for e in lst:
                self._upsert(e)

    def match(self, fltr, n=0) -> list:
        r = []
        with self._lock:
            for v in self.db.values():
                if 0 < n < len(r):
                    break
                if fltr(v.__dict__):
                    r.append(v)
        return r

    def find(self, query: dict, n=0) -> list:
        def fltr(v: dict):
            return self.k_v_match(v, query)
        return self.match(fltr, n)

    def find_by_uuid(self, uuid):
        return self.db.get(uuid)

    def find_one(self, query: dict):
        r = self.find(query, 1)
        if len(r) > 0:
            return r[0]
        return None

    def find_after(self, timestamp: datetime, key="created", n=0) -> list:
        def fltr(v: dict):
            return v[key] > timestamp
        return self.match(fltr, n)

    def find_before(self, timestamp: datetime, key="created", n=0) -> list:
        def fltr(v: dict):
            return v[key] < timestamp
        return self.match(fltr, n)

    def find_contains(self, key: str, value: str, n=0):
        def fltr(v: dict):
            return value in v[key]
        return self.match(fltr, n)

    def find_startswith(self, key: str, value: str, n=0):
        def fltr(v: dict):
            return v[key].startswith(value)
        return self.match(fltr, n)

    def find_endswith(self, key: str, value: str, n=0):
        def fltr(v: dict):
            return v[key].endswith(value)
        return self.match(fltr, n)

    def find_all_with_key(self, key: str, n=0):
        def fltr(v: dict):
            return key in v.keys()
        return self.match(fltr, n)

    def size(self):
        return len(self.db.keys())

    def contains(self, query: dict):
        return self.find_one(query) is not None

    def get_columns(self) -> list:
        r = []
        with self._lock:
            for item in self.db.values():
                for key in item.__dict__.keys():
                    if key not in r:
                        r.append(key)
        return r

    def drop(self):
        with self._lock:
            self.db.clear()
        return self.size() == 0

    def delete(self, fltr: dict):
        r = 0
        for i in self.find(fltr):
            with self._lock:
                del self.db[i.uuid]
            r += 1
        return r > 0

    def delete_by_uuid(self, uuid: str):
        if uuid in self.db.keys():
            with self._lock:
                del self.db[uuid]
            return True
        return False

    def delete_before(self, before: datetime, key="created") -> int:
        r = 0
        for i in self.find_after(before, key):
            with self._lock:
                self.db.pop(i.uuid)
            r += 1
        return r

    def get_all(self):
        return self.db.items()
