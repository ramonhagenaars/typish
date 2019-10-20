from typing import Callable, List, Set, Sequence
from unittest import TestCase

from tests.resources import some_module
from typish._classes import Something, GenericCollectionType

Inyerface = Something[{
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


class TestSomething(TestCase):
    def test_something_with_slices(self):
        self.assertEqual(Inyerface, Something['a': int, 'b': Callable[[int, int], str]])

    def test_something_instance_check(self):
        self.assertTrue(isinstance(C1(), Inyerface))
        self.assertTrue(isinstance(C2(), Inyerface))
        self.assertTrue(not isinstance(C3(), Inyerface))
        self.assertTrue(not isinstance(C4(), Inyerface))
        self.assertTrue(isinstance(C5(), Inyerface))
        self.assertTrue(isinstance(C6(), Inyerface))

    def test_something_subclass_check(self):
        self.assertTrue(issubclass(C1, Inyerface))
        self.assertTrue(issubclass(C2, Inyerface))
        self.assertTrue(not issubclass(C3, Inyerface))
        self.assertTrue(not issubclass(C4, Inyerface))
        self.assertTrue(issubclass(C5, Inyerface))
        self.assertTrue(issubclass(C6, Inyerface))

    def test_module_something_instance_check(self):
        self.assertTrue(isinstance(some_module, Inyerface))

    def test_something_repr(self):
        self.assertEqual("typish.Something['a': int, 'b': typing.Callable[[int, int], str]]",
                         repr(Inyerface))

    def test_isinstance_generic_collection(self):
        isinstance(List[int], GenericCollectionType)
        isinstance(Set[str], GenericCollectionType)
