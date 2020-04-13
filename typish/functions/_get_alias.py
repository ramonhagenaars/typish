import typing
from functools import lru_cache

from typish._types import T


@lru_cache()
def get_alias(cls: T) -> typing.Optional[T]:
    """
    Return the alias from the ``typing`` module for ``cls``. For example, for
    ``cls=list``, the result would be ``typing.List``. If no alias exists for
    ``cls``, then ``None`` is returned.
    :param cls: the type for which the ``typing`` equivalent is to be found.
    :return: the alias from ``typing``.
    """
    return _alias_per_type.get(cls.__name__, None)


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
