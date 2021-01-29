import dataset
import pickle
from uuid import uuid4
from datetime import datetime


TIMESTAMP_FMT = "%d.%m.%Y %H:%M:%S"


class DBEntry(object):
    def __init__(self, **kwargs):
        self.uuid = str(uuid4())
        self.created = self.get_timestamp()
        self.last_updated = self.created
        self.__dict__.update(kwargs)

    @staticmethod
    def get_timestamp(fmt=TIMESTAMP_FMT):
        return datetime.now().strftime(fmt)


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


class Table(object):
    def __init__(self, table: dataset.Table, serializer: Serializer = Serializer):
        self.table = table
        self.serializer = serializer

    def get_by(self, fltr: dict):
        r = self.table.find_one(**fltr)
        if r:
            r = pickle.loads(r["object"])
        return r

    def get_by_uuid(self, uuid: str):
        return self.get_by({"uuid": uuid})

    def contains(self, key: str, value):
        return self.table.count(**{key: value}) > 0

    def serialize(self, o: DBEntry):
        return self.serializer.serialize(o)

    def serialize_many(self, lst: list[DBEntry]):
        return self.serializer.serialize_many(lst)

    def size(self):
        return len(self.table)

    def count(self, key: str, value):
        return self.table.count(**{key: value})

    def insert(self, o: DBEntry):
        self.table.insert(self.serialize(o))

    def insert_many(self, lst: list[DBEntry]):
        self.table.insert_many(self.serialize_many(lst))

    def update(self, o: DBEntry):
        self.table.update(self.serialize(o), ["uuid"])

    def upsert(self, o: DBEntry):
        self.table.upsert(self.serialize(o), ["uuid"])

    def upsert_many(self, lst: list[DBEntry]):
        self.table.upsert_many(self.serialize_many(lst), ["uuid"])

    def delete(self, o: DBEntry):
        if self.contains("uuid", o.uuid):
            self.table.delete(**{"uuid": o.uuid})
            return True
        return False


class DB(object):
    def __init__(self, name: str):
        self.db = dataset.connect("sqlite:///{}.db".format(name))

    def table(self, name: str) -> Table:
        return Table(self.db[name])

    def t(self, name: str) -> Table:
        return self.table(name)
