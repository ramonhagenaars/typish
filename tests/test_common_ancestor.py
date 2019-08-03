from unittest import TestCase
from typish._functions import common_ancestor, common_ancestor_of_types
from typish._types import NoneType


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

    def test_special_args(self):
        self.assertEqual(NoneType, common_ancestor(None, None))
        self.assertEqual(int, common_ancestor(42))

    def test_invalid(self):
        with self.assertRaises(TypeError):
            common_ancestor()
