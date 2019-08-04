import sys
from typing import List, Tuple, Union, Optional
from unittest import TestCase
from typish._functions import subclass_of
from typish._types import Unknown, NoneType


class A: pass
class B(A): pass
class C(B): pass
class D(C): pass
class E(D): pass
class F(E, str): pass


class TestSubclassOf(TestCase):
    def test_subclass_of(self):
        self.assertTrue(not subclass_of(int, str))
        self.assertTrue(subclass_of(E, A))
        self.assertTrue(subclass_of(str, object))
        self.assertTrue(subclass_of(list, List))
        self.assertTrue(subclass_of(List[int], List[int]))
        self.assertTrue(not subclass_of(List[int], List[str]))
        self.assertTrue(subclass_of(List[List[List[int]]], List[List[List[int]]]))
        self.assertTrue(subclass_of(List[int], List[object]))
        self.assertTrue(not subclass_of(List[object], List[int]))
        self.assertTrue(subclass_of(List[Unknown], List[int]))
        self.assertTrue(not subclass_of('test', str))

    def test_subclass_of_tuple(self):
        self.assertTrue(subclass_of(Tuple[int, int], Tuple[int, ...]))
        self.assertTrue(subclass_of(Tuple[int, int], Tuple[object, ...]))
        self.assertTrue(subclass_of(Tuple[A, B], Tuple[A, ...]))
        self.assertTrue(subclass_of(Tuple[int, int], Tuple[int, int]))
        self.assertTrue(subclass_of(Tuple[int, int], Tuple[object, int]))
        self.assertTrue(not subclass_of(Tuple[int, int], Tuple[str, int]))
        self.assertTrue(not subclass_of(Tuple[int, int], Tuple[int, int, int]))
        self.assertTrue(not subclass_of(Tuple[int, int, int], Tuple[int, int]))

    def test_subclass_of_multiple(self):
        self.assertTrue(subclass_of(F, A))
        self.assertTrue(subclass_of(F, str))
        self.assertTrue(subclass_of(F, A, str))
        self.assertTrue(not subclass_of(F, A, str, int))

    def test_subclass_of_union(self):
        self.assertTrue(subclass_of(F, Union[int, str]))
        self.assertTrue(subclass_of(F, Union[A, int]))
        self.assertTrue(subclass_of(F, Union[A, B]))
        self.assertTrue(not subclass_of(int, Union[A, B]))
        self.assertTrue(subclass_of(F, Optional[A]))
        self.assertTrue(subclass_of(NoneType, Optional[A]))

    def test_union_subclass_of(self):
        if sys.version_info[1] in (5, 6):
            with self.assertRaises(TypeError):
                self.assertTrue(subclass_of(Union[int, A, B, F], Union[C, D]))
        else:
            self.assertTrue(subclass_of(Union[int, F], A))
            self.assertTrue(subclass_of(Union[B, F], A))
            self.assertTrue(not subclass_of(Union[A, B], C))

            self.assertTrue(not subclass_of(Union[A, B], Union[C, D]))
            self.assertTrue(subclass_of(Union[int, A, B, F], Union[C, D]))
