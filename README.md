
# podb

[![Build Status](https://build.eberlein.io/buildStatus/icon?job=python_podb)](https://build.eberlein.io/view/python/job/python_podb/)
[![Maintainability](https://api.codeclimate.com/v1/badges/4c7092020ba5916cd90b/maintainability)](https://codeclimate.com/github/nbdy/podb/maintainability)

## (p)ython (o)bject (d)ata(b)ase

thread safe, file based, redis style database for python objects

## reasons not to use this
- you want a database cluster
- you have multiple millions or billions of database entries and limited storage space
- you need relationships / multiple tables

## reasons to use this

- [X] pure python
- [X] cross-platform (Tested: Windows & Linux)
- [X] [thread safe](tests/threaded.py)
- [X] stores python objects
- [X] filters, see below
- [X] [inserting 200 objects takes ~0.0003 seconds](tests/all.py#L74) (i7-4702MQ)
    - size of db with 800 objects is ~600kB 
- [X] ~180 loc
- [X] no extra package dependencies
- [X] [tes](tests/all.py)[ted](tests/huge.py) (Ryzen 7 2700X)
  - [X] [8-8.3k inserts per second](tests/huge.py) 
  - [X] 1000000 entry db is 672MB
    - [mongodb 1 mil collection is 143MB](tests/mongocomp.py)
  - [X] 1000000 entries in 2:04 minutes
    - [mongodb inserts @ 2-2.3k per sec](tests/mongocomp.py)

## functions

- find
- find_one
- find_after
- find_before
- find_by_uuid
- find_contains
- find_startswith
- find_endswith
- insert
- insert_many
- update
- update_many
- upsert
- upsert_many
- size
- contains
- columns
- drop
- remove / delete
- remove_by_uuid / delete_by_uuid
- delete_before
- all

## example

```python
from podb import DB, DBEntry


class Company(DBEntry):
    def __init__(self, name: str):
        DBEntry.__init__(self)
        self.name = name

class Customer(DBEntry):
    def __init__(self, first_name: str, last_name: str, age: int,
                 height: float, companies: list[DBEntry]):
        DBEntry.__init__(self)
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.height = height
        self.companies = companies

db = DB("customers")

c0 = Customer("Jeff", "Bezoz", 42, 1.69,
              [Company("Whole Foods"), Company("Zappos"),
               Company("Ring"), Company("twitch")])
db.insert(c0)

c0 = db.find_one({
    "first_name": "Jeff",
    "last_name": "Bezoz"
})

c0.companies.append(Company("Audible"))

db.update(c0)
```

## installation

```shell
pip3 install podb
```