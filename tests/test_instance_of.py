from typing import List, Dict, Union, Optional, Callable, Any, Tuple, Type, Iterable
from unittest import TestCase

from typish import Literal
from typish._functions import instance_of


class A: pass
class B(A): pass
class C(B): pass
class D(C): pass
class E(D): pass
class F(E, str): pass


class TestInstanceOf(TestCase):
    def test_instance_of(self):
        self.assertTrue(instance_of([[[1], [2]]], List[List[List[int]]]))
        self.assertTrue(instance_of([[[1], ['2']]], List[List[List[object]]]))
        self.assertTrue(instance_of([], List[int]))
        self.assertTrue(instance_of({}, Dict[int, int]))

    def test_instance_of_multiple(self):
        self.assertTrue(instance_of(F(), A))
        self.assertTrue(instance_of(F(), str))
        self.assertTrue(instance_of(F(), A, str))
        self.assertTrue(not instance_of(F(), A, str, int))

    def test_instance_of_union(self):
        self.assertTrue(instance_of(F(), Union[int, A]))
        self.assertTrue(instance_of(F(), Union[A, int]))
        self.assertTrue(instance_of(F(), Union[A, str]))
        self.assertTrue(instance_of(F(), Optional[str]))
        self.assertTrue(instance_of(None, Optional[str]))
        self.assertTrue(instance_of(Any, Union[int, Literal[Any]]))

    def test_instance_of_callable(self):
        def func1(x: int, y: str) -> object:
            pass

        def func2() -> int:
            pass

        def func3(x: int):
            pass

        def func4():
            pass

        def func5(x):
            pass

        def func6(l: List[List[List[int]]]):
            pass

        self.assertTrue(instance_of(func1, Callable[[int, str], object]))
        self.assertTrue(instance_of(func1, Callable[[object, str], object]))
        self.assertTrue(not instance_of(func1, Callable[[str, str], object]))
        self.assertTrue(not instance_of(func1, Callable[[str, str], int]))
        self.assertTrue(instance_of(func2, Callable[[], int]))
        self.assertTrue(instance_of(func3, Callable[[int], Any]))
        self.assertTrue(instance_of(func4, Callable))
        self.assertTrue(instance_of(func5, Callable[[Any], Any]))
        self.assertTrue(instance_of(func6, Callable[[List[List[List[int]]]], Any]))

    def test_lambda_instance_of_callable(self):
        self.assertTrue(instance_of(lambda x, y: 42, Callable[[int, str], str]))
        self.assertTrue(instance_of(lambda: 42, Callable[[], str]))

    def test_instance_of_type(self):
        self.assertTrue(instance_of(int, Type))
        self.assertTrue(instance_of(int, Type[int]))
        self.assertTrue(not instance_of(str, Type[int]))

    def test_instance_of_tuple(self):
        self.assertTrue(instance_of((1,), Tuple[int]))
        self.assertTrue(instance_of((1, 2, 3), Tuple[int, ...]))

    def test_instance_of_list_with_union(self):
        self.assertTrue(instance_of([1, '2', 3], List[Union[int, str]]))
        self.assertTrue(not instance_of([1, '2', 3], List[Union[int, float]]))

    def test_instance_of_tuple_with_union(self):
        self.assertTrue(instance_of((1, '2', 3), Tuple[Union[int, str], ...]))
        self.assertTrue(not instance_of((1, '2', 3), Tuple[Union[int, float], ...]))

    def test_instance_of_iterable(self):
        self.assertTrue(instance_of([1, 2, 3], Iterable[int]))
        self.assertTrue(instance_of((1, 2, 3), Iterable[int]))

    def test_instance_of_literal(self):
        self.assertTrue(instance_of(42, Literal[42]))
        self.assertTrue(instance_of(42, Literal[42], int))
        self.assertTrue(not instance_of(43, Literal[42]))
        self.assertTrue(not instance_of(42, Literal[42], str))
        self.assertTrue(not instance_of(42, Literal))
        self.assertTrue(instance_of(Any, Literal[Any]))
        self.assertTrue(not instance_of(42, Literal[Any]))
