
# podb

[![Build Status](https://build.eberlein.io/buildStatus/icon?job=python_podb)](https://build.eberlein.io/view/python/job/python_podb/)
[![Maintainability](https://api.codeclimate.com/v1/badges/4c7092020ba5916cd90b/maintainability)](https://codeclimate.com/github/nbdy/podb/maintainability)

## (p)ython (o)bject (d)ata(b)ase

thread safe, file based, redis style database for python objects<br>
<details><summary></summary>

it really just is [shelve](https://docs.python.org/3/library/shelve.html) with a hat on

</details>

## reasons not to use this

- you want a database cluster
- you have multiple billions of database entries and limited storage space
- you need relationships

## reasons to use this

- [X] pure python
- [X] cross-platform (Tested: Windows & Linux)
- [X] [fast](tests/huge.py)
  - [inserting 200 objects takes](tests/all.py#L74)
    - ~0.0003 seconds (i7-4702MQ)
    - ~0.0001 seconds (Ryzen 9 3900xt)
  - [X] 8-8.3k inserts per second (Ryzen 7 2700X)
  - [X] 19k inserts per second (Ryzen 9 3900xt)
- [X] [thread safe](tests/threaded.py)
- [X] stores python objects
- [X] filters, see below
- [X] ~180 loc

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
- delete
- delete_by_uuid
- delete_before
- get_all
- get_random
- get_random_list

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