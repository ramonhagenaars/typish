from collections import deque, defaultdict
from collections.abc import Set
from typing import (
    Dict,
    List,
    Tuple,
    FrozenSet,
    Deque,
    DefaultDict,
    Type,
    AbstractSet,
    Set as TypingSet
)
from unittest import TestCase

from typish import get_origin, get_alias


class Union:
    """To shadow typing.Union."""


class MetaMock(type):
    __name__ = 'list'
    __args__ = (str,)


class ListMock(metaclass=MetaMock):
    ...


class TestOriginAndAlias(TestCase):
    def test_get_origin(self):
        self.assertEqual(list, get_origin(List[int]))
        self.assertEqual(tuple, get_origin(Tuple[int, ...]))
        self.assertEqual(dict, get_origin(Dict[str, int]))
        self.assertEqual(set, get_origin(TypingSet))
        self.assertEqual(deque, get_origin(Deque))
        self.assertEqual(defaultdict, get_origin(DefaultDict))
        self.assertEqual(type, get_origin(Type[int]))
        self.assertEqual(Set, get_origin(AbstractSet))
        self.assertIn('test_origin_and_alias', str(get_origin(Union)))

        try:
            self.assertEqual(dict, get_origin(dict[str, str]))
            self.assertEqual(list, get_origin(list[int]))
        except TypeError as err:
            ...  # On <3.9

    def test_get_alias(self):
        self.assertEqual(List, get_alias(list))
        self.assertEqual(Tuple, get_alias(tuple))
        self.assertEqual(Dict, get_alias(dict))
        self.assertEqual(TypingSet, get_alias(set))
        self.assertEqual(FrozenSet, get_alias(frozenset))
        self.assertEqual(Deque, get_alias(deque))
        self.assertEqual(DefaultDict, get_alias(defaultdict))
        self.assertEqual(Type, get_alias(type))
        self.assertEqual(AbstractSet, get_alias(Set))
        self.assertEqual(List, get_alias(List))
        self.assertEqual(Dict, get_alias(Dict))

    def test_get_alias_from_parameterized_standard_list(self):
        self.assertEqual(List[str], get_alias(ListMock))
