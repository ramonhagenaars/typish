import sys
from typing import List, Tuple, Union, Optional, Iterable, Any
from unittest import TestCase

from typish import Literal, subclass_of, Unknown, NoneType


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
        self.assertTrue(subclass_of(Tuple[int, ...], Tuple[int, ...]))
        self.assertTrue(subclass_of(Tuple[int, int], Tuple[object, ...]))
        self.assertTrue(subclass_of(Tuple[int, ...], Tuple[object, ...]))
        self.assertTrue(subclass_of(Tuple[A, B], Tuple[A, ...]))
        self.assertTrue(subclass_of(Tuple[int, int], Tuple[int, int]))
        self.assertTrue(subclass_of(Tuple[int, int], Tuple[object, int]))
        self.assertTrue(not subclass_of(Tuple[int, int], Tuple[str, int]))
        self.assertTrue(not subclass_of(Tuple[int, int], Tuple[int, int, int]))
        self.assertTrue(not subclass_of(Tuple[int, int, int], Tuple[int, int]))
        self.assertTrue(not subclass_of(Tuple[int, str], Tuple[int, ...]))

    def test_list_subclass_of_tuple(self):
        self.assertTrue(not subclass_of(List[int], Tuple[int, ...]))
        self.assertTrue(not subclass_of(List[int], Tuple[int, int]))

    def test_tuple_subclass_of_list(self):
        self.assertTrue(not subclass_of(Tuple[int, ...], List[int]))

    def test_subclass_of_iterable(self):
        self.assertTrue(subclass_of(List[int], Iterable[int]))
        self.assertTrue(subclass_of(Tuple[int, int, int], Iterable[int]))
        self.assertTrue(subclass_of(Tuple[int, ...], Iterable[int]))
        self.assertTrue(subclass_of(Tuple[B, C, D], Iterable[B]))
        self.assertTrue(subclass_of(Tuple[B, C, D], Iterable[A]))
        self.assertTrue(subclass_of(List[Tuple[int, str]], Iterable[Tuple[int, str]]))
        self.assertTrue(subclass_of(Tuple[Tuple[int, str]], Iterable[Tuple[int, str]]))

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

    def test_union_subclass_of_union(self):
        # Subclass holds if all elements of the first enum subclass any of
        # the right enum.
        self.assertTrue(subclass_of(Union[C, D], Union[A, B]))

        # int is no subclass of any of Union[A, B].
        self.assertTrue(not subclass_of(Union[C, D, int], Union[A, B]))

    def test_union_subclass_of(self):
        if sys.version_info[1] in (5,):
            self.assertTrue(not subclass_of(Union[int, A, B, F], Union[C, D]))
        else:
            self.assertTrue(subclass_of(Union[B, F], A))
            self.assertTrue(not subclass_of(Union[A, B], C))
            self.assertTrue(not subclass_of(Union[A, B], Union[C, D]))

    def test_subclass_of_literal(self):
        self.assertTrue(subclass_of(int, Literal[int]))
        self.assertTrue(subclass_of(Any, Literal[Any]))
        self.assertTrue(not subclass_of(int, Literal[Any]))
        self.assertTrue(not subclass_of(int, Literal))
