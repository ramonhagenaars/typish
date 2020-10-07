from sys import version_info
from typing import List, Dict, Union, Optional, Callable, Any, Tuple, Type, Iterable
from unittest import TestCase, skipUnless

import nptyping as nptyping
import numpy

from typish import Literal, instance_of, State, register_get_type


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
        self.assertTrue(not instance_of(42, Literal))
        self.assertTrue(instance_of(2, Literal[1, 2]))

    def test_instance_of_typing_literal(self):
        # This is to mock Python 3.8 Literal.
        class LiteralMockMeta(type):
            __name__ = 'Literal'

            def __instancecheck__(self, instance):
                raise Exception('typing.Literal does not allow instance checks.')

        class LiteralMock(metaclass=LiteralMockMeta):
            __args__ = (42,)

        self.assertTrue(instance_of(42, LiteralMock))

    def test_instance_of_numpy(self):
        self.assertTrue(instance_of(numpy.array([1, 2, 3]), numpy.ndarray))

    def test_instance_of_nptyping_ndarray(self):
        local_state = State()
        register_get_type(numpy.ndarray, nptyping.NDArray.type_of, local_state)

        arr = numpy.array([1, 2, 3])
        arr_type = nptyping.NDArray[(3,), int]

        self.assertTrue(instance_of(arr, arr_type, state=local_state))
        self.assertTrue(instance_of([arr], List[arr_type], state=local_state))
        self.assertTrue(instance_of([arr], List[nptyping.NDArray], state=local_state))
        self.assertTrue(not instance_of([arr], List[nptyping.NDArray[(4,), float]], state=local_state))

    @skipUnless(10 * version_info.major + version_info.minor >= 39, 'PEP-585')
    def test_instance_of_py39_types(self):
        self.assertTrue(instance_of({'42': 42}, Dict[str, int]))
        self.assertTrue(not instance_of({'42': 42}, Dict[str, str]))
        self.assertTrue(not instance_of({42: 42}, Dict[str, int]))
        self.assertTrue(instance_of([1, 2, 3], list[int]))
        self.assertTrue(not instance_of([1, 2, 3], list[str]))
