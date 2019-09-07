from unittest import TestCase
from typish._classes import SubscriptableType


class TestSubscriptableType(TestCase):
    def test_subscribing(self):

        class C(metaclass=SubscriptableType):
            ...

        self.assertEqual('arg', C['arg'].__args__)
        self.assertEqual(C, C['arg'].__origin__)
