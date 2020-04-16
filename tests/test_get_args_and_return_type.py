from typing import Callable
from unittest import TestCase

from typish import NoneType, get_args_and_return_type


class TestGetArgsAndReturnType(TestCase):
    def test_get_args_and_return_type(self):
        arg_types, return_type = get_args_and_return_type(
        Callable[[int, str], float])

        self.assertEqual((int, str), arg_types)
        self.assertEqual(float, return_type)

    def test_get_args_and_return_type_no_args(self):
        arg_types, return_type = get_args_and_return_type(
            Callable[[], float])

        self.assertEqual(tuple(), arg_types)
        self.assertEqual(float, return_type)

    def test_get_args_and_return_type_no_return_type(self):
        arg_types, return_type = get_args_and_return_type(
            Callable[[int, str], None])

        self.assertEqual((int, str), arg_types)
        self.assertEqual(NoneType, return_type)

    def test_get_args_and_return_type_no_hints(self):
        arg_types1, return_type1 = get_args_and_return_type(Callable)
        arg_types2, return_type2 = get_args_and_return_type(callable)

        self.assertEqual(None, arg_types1)
        self.assertEqual(None, return_type1)
        self.assertEqual(None, arg_types2)
        self.assertEqual(None, return_type2)
