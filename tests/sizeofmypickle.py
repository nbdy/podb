import pickle


class DBEntry(object):
    def __init__(self, **kwargs):
        self.data = "lsknflas"


class Jeff(DBEntry):
    def __init__(self, **kwargs):
        DBEntry.__init__(self, **kwargs)
        self.data = "lk lksnls dfas"


if __name__ == '__main__':
    p1 = pickle.dumps(DBEntry())
    p2 = pickle.dumps(Jeff())
    print(len(p1), len(p2))
