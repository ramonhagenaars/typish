from typing import Type
from unittest import TestCase

from typish import common_ancestor, common_ancestor_of_types, NoneType


class A: pass
class B(A): pass
class C(B): pass
class D(C): pass
class E(D): pass


class TestCommonAncestor(TestCase):
    def test_common_ancestor(self):
        self.assertEqual(C, common_ancestor(E(), C(), D(), E()))
        self.assertEqual(B, common_ancestor(E(), C(), D(), E(), B()))
        self.assertEqual(object, common_ancestor(E(), C(), D(), E(), B(), 42))

    def test_common_ancestor_of_types(self):
        self.assertEqual(C, common_ancestor_of_types(E, C, D, E))
        self.assertEqual(object, common_ancestor_of_types(int, str))
        common_ancestor_of_types(list, tuple)

    def test_common_ancestor_of_typing_types(self):
        self.assertEqual(type, common_ancestor_of_types(Type[int], Type[str]))

    def test_common_acestor_of_collections(self):
        self.assertEqual(list, common_ancestor([1, 2, 3], ['a', 'b', 'c']))

    def test_special_args(self):
        self.assertEqual(NoneType, common_ancestor(None, None))
        self.assertEqual(int, common_ancestor(42))

    def test_invalid(self):
        with self.assertRaises(TypeError):
            common_ancestor()
