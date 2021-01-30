import dataset
import pickle
from multiprocessing import Lock
from uuid import uuid4
from datetime import datetime


class DBEntry(object):
    def __init__(self, **kwargs):
        self.uuid = str(uuid4())
        self.created = self.get_timestamp()
        self.last_updated = self.created
        self.__dict__.update(kwargs)

    @staticmethod
    def get_timestamp():
        return datetime.now().isoformat()


class Serializer(object):
    @staticmethod
    def serialize(obj: DBEntry):
        ctx = {
            "object": pickle.dumps(obj),
            # "functions": []
        }
        for k, v in obj.__dict__.items():
            for t in [str, int, float, bytes, bool, complex]:
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
    mtx = Lock()
    ser: Serializer = None

    def __init__(self, name: str, serializer: Serializer = Serializer):
        self.ser = serializer
        self.db = dataset.connect("sqlite:///{}.db".format(name), engine_kwargs={"connect_args":
                                                                                     {"check_same_thread": False}})

    def _exec(self, f, args, kwargs):
        with self.mtx:
            r = f(*args, **kwargs)
        return r

    def _query(self, qry: str, params):
        return self._exec(self.db.query, [qry], params)

    def _t(self, n: str) -> dataset.Table:
        return self.db[n]

    def get_by(self, tbl: str, fltr: dict):
        r = self._exec(self._t(tbl).find_one, [], fltr)
        if r:
            r = pickle.loads(r["object"])
        return r

    def get_by_uuid(self, tbl: str, uuid: str):
        return self.get_by(tbl, {"uuid": uuid})

    def get_after(self, tbl: str, after: str):
        return self._query("select * from :tbl where last_updated >= date(:ts);", {
            "tbl": tbl, "ts": after
        })

    def contains(self, tbl: str, key: str, value):
        return self._exec(self._t(tbl).count, [], {key: value}) > 0

    def serialize(self, o: DBEntry):
        return self.ser.serialize(o)

    def serialize_many(self, lst: list[DBEntry]):
        return self.ser.serialize_many(lst)

    def size(self, tbl: str):
        return len(self._t(tbl))

    def count(self, tbl: str, key: str, value):
        return self._exec(self._t(tbl).count, [], {key: value})

    def insert(self, tbl: str, o: DBEntry):
        self._exec(self._t(tbl).insert, [self.serialize(o)], {})

    def insert_many(self, tbl: str, lst: list[DBEntry]):
        self._exec(self._t(tbl).insert_many, [self.serialize_many(lst)], {})

    def update(self, tbl: str, o: DBEntry):
        self._exec(self._t(tbl).update, [self.serialize(o), ["uuid"]], {})

    def upsert(self, tbl: str, o: DBEntry):
        self._exec(self._t(tbl).upsert, [self.serialize(o), ["uuid"]], {})

    def upsert_many(self, tbl: str, lst: list[DBEntry]):
        self._exec(self._t(tbl).upsert_many, [self.serialize_many(lst), ["uuid"]], {})

    def delete(self, tbl: str, o: DBEntry):
        self._exec(self._t(tbl).delete, [], {"uuid": o.uuid})
