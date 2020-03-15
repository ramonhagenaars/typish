from unittest import TestCase

from typish import get_type_hints_of_callable


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
