import pickle
from multiprocessing import Lock
from uuid import uuid4
import dataset
from datetime import datetime


FMT_TIMESTAMP = "%Y.%m.%d %H:%M:%S"


class DBEntry(object):
    def __init__(self, **kwargs):
        self.uuid = str(uuid4())
        self.created = self.get_timestamp()
        self.last_modified = self.created
        self.__dict__.update(kwargs)

    @staticmethod
    def get_timestamp(fmt=FMT_TIMESTAMP):
        return datetime.now().strftime(fmt)


class Serializer(object):
    @staticmethod
    def serialize(obj: DBEntry):
        ctx = {
            "object": pickle.dumps(obj),
            # "functions": []
        }
        for k, v in obj.__dict__.items():
            for t in [str, int, float, bytes, bool, complex, datetime]:
                if isinstance(v, t):
                    ctx[k] = v
            '''
            if hasattr(v, '__call__'):
                ctx.__setitem__("functions", v.__name__)
                # ctx["functions"].append(v.__name__)
            elif isinstance(v, dict):
                ctx[k] = DB.serialize(v)
            elif isinstance(v, object):
                ctx[k] = DB.serialize(v.__dict__)
            '''
        return ctx

    @classmethod
    def serialize_many(cls, lst: list[DBEntry]):
        r = []
        for i in lst:
            r.append(cls.serialize(i))
        return r


class DB(object):
    mtx: Lock = Lock()
    ser: Serializer = None

    def __init__(self, name: str, serializer: Serializer = Serializer):
        self.ser = serializer
        self.db = dataset.connect("sqlite:///{}.db".format(name),
                                  engine_kwargs={"connect_args": {"check_same_thread": False}})

    @staticmethod
    def get_object(r):
        if r:
            return pickle.loads(r["object"])
        return None

    def get_by(self, tbl: str, key: str, value):
        r = []
        for i in self.db[tbl].find(**{key: value}):
            r.append(self.get_object(i))
        return r

    def get_one_by(self, tbl: str, key: str, value):
        return self.get_object(self.db[tbl].find_one(**{key: value}))

    def get_by_uuid(self, tbl: str, uuid: str):
        return self.get_one_by(tbl, "uuid", uuid)

    def get_after(self, tbl: str, after: datetime, count: int = 10):
        with self.mtx:
            t = self.db[tbl]
            d = t.find(t.table.columns.last_modified >= after.strftime(FMT_TIMESTAMP), _limit=count,
                       order_by=["last_modified"])
        r = []
        for i in d:
            r.append(self.get_object(i))
        return r

    def contains(self, tbl: str, key: str, value):
        with self.mtx:
            r = self.db[tbl].count(**{key: value})
        return r > 0

    def serialize(self, o: DBEntry):
        return self.ser.serialize(o)

    def serialize_many(self, lst: list[DBEntry]):
        return self.ser.serialize_many(lst)

    def size(self, tbl: str):
        with self.mtx:
            r = self.db[tbl].count(**{})
        return r

    def get_tables(self):
        return self.db.tables

    def get_columns(self, tbl: str):
        return self.db[tbl].columns

    def count(self, tbl: str, key: str, value):
        with self.mtx:
            r = self.db[tbl].count(**{key: value})
        return r

    def insert(self, tbl: str, o: DBEntry):
        with self.mtx:
            self.db[tbl].insert(self.serialize(o))

    def insert_many(self, tbl: str, lst: list[DBEntry]):
        with self.mtx:
            self.db[tbl].insert_many(self.serialize_many(lst))

    def update(self, tbl: str, o: DBEntry):
        with self.mtx:
            self.db[tbl].update(self.serialize(o), ["uuid"])

    def upsert(self, tbl: str, o: DBEntry):
        with self.mtx:
            self.db[tbl].upsert(self.serialize(o), ["uuid"])

    def upsert_many(self, tbl: str, lst: list[DBEntry]):
        with self.mtx:
            self.db[tbl].upsert_many(self.serialize_many(lst), ["uuid"])

    def remove(self, tbl: str, o: DBEntry):
        with self.mtx:
            self.db[tbl].delete(**{"uuid": o.uuid})
