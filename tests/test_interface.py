from typing import Callable, List, Set
from unittest import TestCase

from tests.resources import some_module
from typish._classes import Interface, GenericCollection


Inyerface = Interface[{  # :-D
    'a': int,
    'b': Callable[[int, int], str],
}]


class C1:
    a = 42

    def b(self, a: int, b: int) -> str:
        return str(a + b)


class C2:
    def __init__(self):
        self.a = 42

    def b(self, a: int, b: int) -> str:
        return str(a + b)


class C3:
    def __init__(self):
        self.a = 42

    def b(self, a, b):
        return str(a + b)


class C4:
    def __init__(self):
        self.a = 42

    def b(self, a, b: str):
        return str(a + b)


class C5:
    a = 42

    @staticmethod
    def b(a: int, b: int) -> str:
        return str(a + b)


class C6:
    a = 42

    @classmethod
    def b(cls, a: int, b: int) -> str:
        return str(a + b)


class TestInterface(TestCase):
    def test_interface_instance_check(self):
        self.assertTrue(isinstance(C1(), Inyerface))
        self.assertTrue(isinstance(C2(), Inyerface))
        self.assertTrue(not isinstance(C3(), Inyerface))
        self.assertTrue(not isinstance(C4(), Inyerface))
        self.assertTrue(isinstance(C5(), Inyerface))
        self.assertTrue(isinstance(C6(), Inyerface))

    def test_module_interface_instance_check(self):
        self.assertTrue(isinstance(some_module, Inyerface))

    def test_isinstance_generic_collection(self):
        isinstance(List[int], GenericCollection)
        isinstance(Set[str], GenericCollection)
