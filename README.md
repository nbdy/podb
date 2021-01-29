# podb
### (p)ython (o)bject (d)ata(b)ase
mongo style database for python objects
## indexed types
- str
- int
- float 
- bytes
- bool
- complex
## procedure
- saves supported data types as columns
- pickles the actual object and saves that as a string
- when select matches one of the columns, the object is unpickled and returned
## functions
- get_by
- get_by_uuid
- contains
- insert
- insert_many
- update
- upsert
- upsert_many
- size
## indexed datatypes
## example
```python
from podb import DB, DBEntry


class Company(DBEntry):
    def __init__(self, name: str):
        self.name = name

class Customer(DBEntry):
    def __init__(self, first_name: str, last_name: str, age: int, height: float, companies: list[DBEntry]):
        DBEntry.__init__(self)
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.height = height
        self.companies = companies

db = DB("customers")
tbl = db.t("private_data")  # or db.table()

c0 = Customer("Jeff", "Bezoz", 42, 1.69, 
              [Company("Whole Foods"), Company("Zappos"), 
               Company("Ring"), Company("twitch")])
tbl.insert(c0)

c0 = tbl.get_by({
    "first_name": "Jeff",
    "last_name": "Bezoz"
})

c0.companies.append(Company("Audible"))

tbl.update(c0)
```
## installation
```shell
pip3 install git+https://github.com/nbdy/podb
```