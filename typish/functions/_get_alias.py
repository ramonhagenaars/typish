import typing
from functools import lru_cache

from typish.functions._is_from_typing import is_from_typing

from typish._types import T


@lru_cache()
def get_alias(cls: T) -> typing.Optional[T]:
    """
    Return the alias from the ``typing`` module for ``cls``. For example, for
    ``cls=list``, the result would be ``typing.List``. If ``cls`` is
    parameterized (>=3.9), then a parameterized ``typing`` equivalent is
    returned. If no alias exists for ``cls``, then ``None`` is returned.
    If ``cls`` already is from ``typing`` it is returned as is.
    :param cls: the type for which the ``typing`` equivalent is to be found.
    :return: the alias from ``typing``.
    """
    if is_from_typing(cls):
        return cls
    alias = _alias_per_type.get(cls.__name__, None)
    if alias:
        args = getattr(cls, '__args__', tuple())
        if args:
            alias = alias[args]
    return alias


_alias_per_type = {
    'list': typing.List,
    'tuple': typing.Tuple,
    'dict': typing.Dict,
    'set': typing.Set,
    'frozenset': typing.FrozenSet,
    'deque': typing.Deque,
    'defaultdict': typing.DefaultDict,
    'type': typing.Type,
    'Set': typing.AbstractSet,
}
