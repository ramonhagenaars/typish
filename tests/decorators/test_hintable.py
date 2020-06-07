import sys
from typing import Type
from unittest import TestCase

from typish import hintable, T

if sys.version_info.major * 10 + sys.version_info.minor > 35:
    # All Python 3.5+ specific tests are moved to a separate module.
    from test_resources.hintable import TestHintable as Base
else:
    Base = TestCase


@hintable
def some_func(hint: Type[T]) -> Type[T]:
    """Some docstring"""
    return hint


class TestHintable(Base):
    def test_hintable_without_any_hint(self):
        # Test that when a hintable function is called without hint, it
        # receives None.

        x = some_func()

        self.assertEqual(None, x)

    def test_hintable_class(self):
        # Test that decorating a class raises an error.

        with self.assertRaises(TypeError):
            @hintable
            class DecoratedClass:
                ...

    def test_meta_data(self):
        # Test that any meta data is copied properly.

        self.assertEqual('Some docstring', some_func.__doc__)

    def test_hintable_with_flawed_function(self):

        with self.assertRaises(TypeError):
            @hintable
            def some_flawed_func():
                ...

    def test_hintable_with_flawed_custom_param_name(self):
        # Test that when a custom param name is used, it is checked if a
        # parameter with that name is accepted by the decorated function.

        with self.assertRaises(TypeError):
            @hintable(param='cls')
            def some_func_with_flawed_custom_param_name(hint):
                return hint
