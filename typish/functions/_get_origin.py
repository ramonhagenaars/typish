import typing
from collections import deque, defaultdict
from collections.abc import Set
from inspect import isclass

from typish.functions._is_from_typing import is_from_typing


def get_origin(t: type) -> type:
    """
    Return the origin of the given (generic) type. For example, for
    ``t=List[str]``, the result would be ``list``.
    :param t: the type of which the origin is to be found.
    :return: the origin of ``t`` or ``t`` if it is not generic.
    """
    from typish.functions._get_simple_name import get_simple_name

    simple_name = get_simple_name(t)
    result = _type_per_alias.get(simple_name, None)
    if isclass(t) and not is_from_typing(t):
        # Get the origin in case of a parameterized generic.
        result = getattr(t, '__origin__', t)
    elif not result:
        result = getattr(typing, simple_name, t)
    return result


_type_per_alias = {
    'List': list,
    'Tuple': tuple,
    'Dict': dict,
    'Set': set,
    'FrozenSet': frozenset,
    'Deque': deque,
    'DefaultDict': defaultdict,
    'Type': type,
    'AbstractSet': Set,
    'Optional': typing.Union,
}
