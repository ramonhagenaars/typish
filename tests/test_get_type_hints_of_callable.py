from typing import Callable
from unittest import TestCase

from typish import get_type_hints_of_callable, get_args_and_return_type


class TestGetTypeHintsOfCallable(TestCase):
    def test_get_type_hints_of_callable(self):

        def func(x: int, y: int) -> str:
            return '{}{}'.format(x, y)

        hints = get_type_hints_of_callable(func)

        self.assertEqual(int, hints['x'])
        self.assertEqual(int, hints['y'])
        self.assertEqual(str, hints['return'])

    def test_get_type_hints_of_empty_callable(self):

        def func():
            return 42

        hints = get_type_hints_of_callable(func)

        self.assertEqual({}, hints)

    def test_get_args_and_return_type(self):
        args, return_type = get_args_and_return_type(Callable[[int, int], str])

        self.assertTupleEqual((int, int), args)
        self.assertEqual(str, return_type)

    def test_get_args_and_return_type_with_explicit_result(self):
        class CallableMock:
            __args__ = (int, int)
            __result__ = str

        args, return_type = get_args_and_return_type(CallableMock)

        self.assertTupleEqual((int, int), args)
        self.assertEqual(str, return_type)

    def test_get_type_hints_of_callable_with_raising_callable(self):
        # Python3.5: get_type_hints raises on classes without explicit constructor
        class CallableMetaMock(type):
            def __getattribute__(self, item):
                raise AttributeError('')

        class CallableMock(metaclass=CallableMetaMock):
            ...

        self.assertEqual({}, get_type_hints_of_callable(CallableMock))
