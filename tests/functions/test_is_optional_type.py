from typing import Optional, Union
from unittest import TestCase

from typish import (
    NoneType,
)
from typish.functions._is_optional_type import is_optional_type


class TestIsOptionalType(TestCase):
    def test_is_optional_type(self):
        self.assertTrue(is_optional_type(Optional[str]))
        self.assertTrue(is_optional_type(Union[str, None]))
        self.assertTrue(is_optional_type(Union[str, NoneType]))
        self.assertTrue(not is_optional_type(str))
        self.assertTrue(not is_optional_type(Union[str, int]))
