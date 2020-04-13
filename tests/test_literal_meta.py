from unittest import TestCase

from typish import LiteralAlias


class TestLiteralMeta(TestCase):
    def test_from_literal(self):

        class LiteralMock:
            __args__ = (42,)

        alias = LiteralAlias.from_literal(LiteralMock)

        self.assertTrue(isinstance(42, alias))

    def test_str(self):
        self.assertEqual('Literal[42]', str(LiteralAlias[42]))
