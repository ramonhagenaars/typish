from unittest import TestCase

from typish import ClsDict
from typish._classes import ClsFunction


class TestClsFunction(TestCase):
    def test_invalid_initialization(self):
        # Only ClsDict or dict is allowed
        with self.assertRaises(TypeError):
            ClsFunction(123)

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
