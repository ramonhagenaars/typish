from typing import Type
from unittest import TestCase

from typish import T, hintable


class C:
    def __init__(self, subject):
        self.subject = subject


@hintable
def cast(subject, hint: Type[T]) -> T:
    return hint(subject)


@hintable
def some_func(hint: Type[T]) -> Type[T]:
    """Some docstring"""
    return hint


@hintable(param='cls')
def some_func_with_custom_param_name(cls):
    return cls


class SomeClass:
    @hintable
    def some_method(self, hint):
        return hint

    @staticmethod
    @hintable
    def some_static_method(hint):
        return hint

    @classmethod
    @hintable
    def some_class_method(cls, hint):
        return hint


class TestHintable(TestCase):
    def test_hintable(self):
        # Test that a function can be decorated and receives a hint.

        x: int = cast('42')
        y: str = cast(42)
        z: '  str  ' = cast(42)  # Even a sloppy hint should work.

        self.assertEqual(42, x)
        self.assertEqual('42', y)
        self.assertEqual('42', z)

    def test_hintable_with_parentheses(self):
        # Test that hintable can be used with parentheses as well.

        @hintable()  # Note the parentheses.
        def some_function(hint):
            return hint

        x: int = some_function()

        self.assertEqual(int, x)

    def test_hintable_with_custom_param_name(self):
        # Test that functions can customize the parameter name that receives
        # the type hint.

        x: int = some_func_with_custom_param_name()

        self.assertEqual(int, x)

    def test_hintable_method(self):
        # Test that methods can be hintable as well.

        sc = SomeClass()
        x: int = sc.some_method()
        y: float = SomeClass.some_static_method()
        z: str = SomeClass.some_class_method()

        self.assertEqual(int, x)
        self.assertEqual(float, y)
        self.assertEqual(str, z)

    def test_hintable_with_custom_type(self):
        # Test that a custom type can be used as hint without a problem.

        x: C = cast(42)
        y: 'C' = cast(42)

        self.assertTrue(isinstance(x, C))
        self.assertTrue(isinstance(y, C))

    def test_hintable_with_textual_hint(self):
        # Test that textual hints are received as strings.

        x: 'some rubbish' = some_func()
        y: "'some even greater rubbish'" = some_func()

        self.assertEqual('some rubbish', x)
        self.assertEqual('\'some even greater rubbish\'', y)

    def test_hintable_with_comment_hint(self):
        # Test that hints in MyPy style work as well.

        x = some_func()  # type: int
        y = some_func()  # type: rubbish_again
        # The type hint should take precedence of MyPy-styled-hints:
        z: int = some_func()  # type: str

        self.assertEqual(int, x)
        self.assertEqual('rubbish_again', y)
        self.assertEqual(int, z)

    def test_override_with_custom_hint(self):
        # Test that you can still override the hint.

        x = some_func(hint=int)
        y: int = some_func(hint=str)  # It's allowed, but is it a good idea?

        self.assertEqual(int, x)
        self.assertEqual(str, y)
