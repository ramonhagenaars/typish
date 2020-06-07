from typing import List
from unittest import TestCase

from typish import (
    is_type_annotation,
    T,
    KT,
    VT,
    Unknown,
    Module,
    NoneType,
    EllipsisType,
    Empty,
)


class TestIsTypeAnnotation(TestCase):
    def test_is_type_annotation(self):
        # builtins and typing.
        self.assertTrue(is_type_annotation(int))
        self.assertTrue(is_type_annotation(List))

        # Typish types.
        self.assertTrue(is_type_annotation(Empty))
        self.assertTrue(is_type_annotation(Unknown))
        self.assertTrue(is_type_annotation(Module))
        self.assertTrue(is_type_annotation(NoneType))
        self.assertTrue(is_type_annotation(EllipsisType))

        # No instances.
        self.assertTrue(not is_type_annotation(123))
        self.assertTrue(not is_type_annotation('No way'))

        # Typevars do not count.
        self.assertTrue(not is_type_annotation(T))
        self.assertTrue(not is_type_annotation(KT))
        self.assertTrue(not is_type_annotation(VT))
