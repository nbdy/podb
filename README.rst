podb
====

(p)ython (o)bject (d)ata(b)ase
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

thread safe redis style database for python objects

reasons to use this
-------------------

-  `thread safe`_
-  stores python objects
-  filters, see below
-  `inserting 200 objects takes ~0.0003 seconds`_ (i7-4702MQ)
-  size of db with 800 objects is ~600kB
-  ~120 loc
-  no extra package dependencies
-  `tes`_\ `ted`_
-  `10-11k inserts per second`_ (i7-4702MQ)

notes
-----

-  `1 million entry db is 1.3GB`_
-  `not multiprocess safe (yet?)`_

functions
---------

-  find
-  find_one
-  find_after
-  find_before
-  find_by_uuid
-  find_contains
-  find_startswith
-  find_endswith
-  insert
-  insert_many
-  update
-  update_many
-  upsert
-  upsert_many
-  size
-  contains
-  columns
-  drop
-  remove / delete
-  remove_by_uuid / delete_by_uuid
-  delete_before

example
-------

.. code:: python

   from podb import DB, DBEntry


   class Company(DBEntry):
       def __init__(self, name: str):
           DBEntry.__init__(self)
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

installation
------------

.. code:: shell

   pip3 install podb

.. _thread safe: tests/threaded.py
.. _inserting 200 objects takes ~0.0003 seconds: tests/all.py#L74
.. _tes: tests/all.py
.. _ted: tests/huge.py
.. _10-11k inserts per second: tests/huge.py
.. _1 million entry db is 1.3GB: tests/huge.db
.. _not multiprocess safe (yet?): tests/processed.py