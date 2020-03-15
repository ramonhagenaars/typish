import typing
from typing import Union
from unittest import TestCase

from typish._functions import _get_mro


class A:
    ...


class B(A):
    ...


class TestGetMRO(TestCase):
    def test_get_mro(self):
        mro_b = _get_mro(B)
        self.assertTupleEqual((B, A, object), mro_b)

    def test_get_mro_union(self):
        mro_u = _get_mro(Union[int, str])

        # Below is to stay compatible with Python 3.5+
        super_cls = getattr(typing, '_GenericAlias',
                            getattr(typing, 'GenericMeta', None))
        expected = (typing.Union, super_cls, object)

        self.assertTupleEqual(expected, mro_u)
