from unittest import TestCase

from typish import __version__


class TestMeta(TestCase):
    def test_meta(self):
        # Test that __version__ is importable and is a string.
        self.assertTrue(isinstance(__version__, str))
