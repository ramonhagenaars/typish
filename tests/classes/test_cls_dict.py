from collections import OrderedDict
from typing import List, Union, Tuple
from unittest import TestCase

from typish import ClsDict


class TestClsDict(TestCase):
    def test_invalid_initialization(self):
        # Only one positional argument is accepted.
        with self.assertRaises(TypeError):
            ClsDict({}, {})

        # The positional argument must be a dict
        with self.assertRaises(TypeError):
            ClsDict(1)

        # The dict must have types as keys
        with self.assertRaises(TypeError):
            ClsDict({
                int: 1,
                str: 2,
                'float': 3,
            })

    def test_getitem(self):
        cd = ClsDict({int: 123, str: '456'})

        self.assertEqual(123, cd[42])
        self.assertEqual('456', cd['test'])

    def test_getitem_more_complicated(self):
        cd = ClsDict({
            List[Union[str, int]]: 1,
            Tuple[float, ...]: 2,
        })
        self.assertEqual(1, cd[[1, 2, '3', 4]])
        self.assertEqual(2, cd[(1.0, 2.0, 3.0, 4.0)])

        with self.assertRaises(KeyError):
            self.assertEqual(2, cd[(1.0, 2.0, '3.0', 4.0)])

    def test_no_match(self):
        cd = ClsDict({str: '456'})

        with self.assertRaises(KeyError):
            cd[42]

    def test_get(self):
        cd = ClsDict({str: '456'})

        self.assertEqual('456', cd.get('test'))
        self.assertEqual(None, cd.get(42))
        self.assertEqual(123, cd.get(42, 123))

    def test_ordereddict(self):
        od = OrderedDict([
            (int, 1),
            (object, 2),
        ])
        cd = ClsDict(od)

        self.assertEqual(1, cd[123])
        self.assertEqual(2, cd['123'])
