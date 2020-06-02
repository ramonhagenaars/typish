from typing import Tuple, Any, Union
from unittest import TestCase

from typish import ClsDict, EllipsisType, Literal, ClsFunction


class TestClsFunction(TestCase):
    def test_invalid_initialization(self):
        # Only ClsDict or dict is allowed
        with self.assertRaises(TypeError):
            ClsFunction(123)

    def test_instantiation_with_no_callable(self):
        with self.assertRaises(TypeError):
            ClsFunction({
                int: lambda: 1,
                str: lambda: 2,
                object: 3,  # Invalid!
            })

    def test_with_dict(self):
        function = ClsFunction({
            int: lambda x: x * 2,
            str: lambda x: '{}_'.format(x),
        })

        self.assertEqual(4, function(2))
        self.assertEqual('2_', function('2'))

    def test_with_cls_dict(self):
        function = ClsFunction(ClsDict({
            int: lambda x: x * 2,
            str: lambda x: '{}_'.format(x),
        }))

        self.assertEqual(4, function(2))
        self.assertEqual('2_', function('2'))

    def test_with_iterable_of_tuples(self):
        body = [
            (int, lambda x: x * 2),
            (str, lambda x: '{}_'.format(x)),
        ]

        function_tuple = ClsFunction(body)
        function_set = ClsFunction(set(body))
        function_list = ClsFunction(list(body))

        self.assertEqual(4, function_tuple(2))
        self.assertEqual('2_', function_tuple('2'))
        self.assertEqual(4, function_set(2))
        self.assertEqual('2_', function_set('2'))
        self.assertEqual(4, function_list(2))
        self.assertEqual('2_', function_list('2'))

    def test_with_callables(self):
        def f1(x: int):
            return 1

        class C:
            def m1(self, x: str):
                return 2

            @classmethod
            def m2(cls, x: float):
                return 3

            @staticmethod
            def m3(x: list):
                return 4

        def f2(x):  # No type hint
            return 5

        function = ClsFunction([f1, C().m1, C.m2, C.m3, f2])
        self.assertEqual(1, function(42))
        self.assertEqual(2, function('hello'))
        self.assertEqual(3, function(42.0))
        self.assertEqual(4, function([42]))
        self.assertEqual(5, function({}))

    def test_with_invalid_callables(self):
        def f():
            ...

        with self.assertRaises(TypeError):
            ClsFunction([f])

    def test_multiple_args(self):
        function = ClsFunction({
            int: lambda x, y: x * y,
            str: lambda x, y: '{}{}'.format(x, y),
        })

        self.assertEqual(6, function(2, 3))
        self.assertEqual('23', function('2', 3))

    def test_understands(self):
        function = ClsFunction({
            int: lambda _: ...,
            str: lambda _: ...,
        })
        self.assertTrue(function.understands(1))
        self.assertTrue(function.understands('2'))
        self.assertTrue(not function.understands(3.0))

    def test_call_no_args(self):
        function = ClsFunction({
            int: lambda x: 1,
        })

        with self.assertRaises(TypeError):
            function()

    def test_call_invalid_args(self):
        function = ClsFunction({
            int: lambda x: 1,
        })

        with self.assertRaises(TypeError):
            function(1, 2)  # The lambda expects only 1 argument.

    def test_complex_cls_function(self):
        # Test if a more complex ClsFunction can be created without problems.
        _Size = Union[int, Literal[Any]]
        _Type = Union[type, Literal[Any]]

        ClsFunction({
            _Size: lambda: 1,
            _Type: lambda: 2,
            Tuple[_Size, _Type]: lambda: 3,
            Tuple[_Size, ...]: lambda: 4,
            Tuple[Tuple[_Size, ...], _Type]: lambda: 5,
            Tuple[Tuple[_Size, EllipsisType], _Type]: lambda: 6,
            Tuple[Tuple[Literal[Any], EllipsisType], Literal[Any]]: lambda: 7,
        })
