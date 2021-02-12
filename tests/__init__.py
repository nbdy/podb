from podb import DBEntry

from random import choice, randint, uniform
from string import printable, ascii_lowercase
from datetime import datetime
from random import choices


def generate_string(n=20, charset=printable):
    return ''.join(choice(charset) for _ in range(n))


class TestObject(DBEntry):
    def __init__(self, name: str, age: int, size: float):
        DBEntry.__init__(self)
        self.name = name
        self.age = age
        self.size = size

    @staticmethod
    def random():
        return TestObject(generate_string(), randint(0, 420), uniform(1.4, 2))


class HugeDBItem(TestObject):
    def __init__(self, name: str, age: int, height: float, weight: float, color: str, birth_date: datetime):
        TestObject.__init__(self, name, age, height * weight)
        self.height = height
        self.weight = weight
        self.color = color
        self.birth_date = birth_date

    @staticmethod
    def random():
        return HugeDBItem(
            ''.join(choices(ascii_lowercase, k=30)),
            randint(1, 99),
            uniform(1.0, 250.0),
            uniform(1.0, 600.0),
            choice(["black", "white", "brown", "really?"]),
            datetime.now()
        )
