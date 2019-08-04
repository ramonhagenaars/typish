"""
PRIVATE MODULE: do not import (from) it directly.

This module contains the implementation of all functions of typish.
"""
import inspect
import sys
import types
import typing
from collections import deque, defaultdict, Set
from functools import lru_cache
from inspect import getmro
from typish._types import T, KT, VT, NoneType, Unknown, Empty


def subclass_of(cls: type, *args: type) -> bool:
    """
    Return whether ``cls`` is a subclass of all types in ``args`` while also
    considering generics.
    :param cls: the subject.
    :param args: the super types.
    :return: True if ``cls`` is a subclass of all types in ``args`` while also
    considering generics.
    """
    if len(args) > 1:
        result = subclass_of(cls, args[0]) and subclass_of(cls, *args[1:])
    else:
        result = _subclass_of(cls, args[0])
    return result


def instance_of(obj: object, *args: type) -> bool:
    """
    Check whether ``obj`` is an instance of all types in ``args``, while also
    considering generics.
    :param obj: the object in subject.
    :param args: the type(s) of which ``obj`` is an instance or not.
    :return: ``True`` if ``obj`` is an instance of all types in ``args``.
    """
    return subclass_of(get_type(obj), *args)


def get_origin(t: type) -> type:
    """
    Return the origin of the given (generic) type. For example, for
    ``t=List[str]``, the result would be ``list``.
    :param t: the type of which the origin is to be found.
    :return: the origin of ``t`` or ``t`` if it is not generic.
    """
    simple_name = _get_simple_name(t)
    result = _type_per_alias.get(simple_name, None)
    if not result:
        result = getattr(typing, simple_name, t)
    return result


def get_args(t: type) -> typing.Tuple[type, ...]:
    """
    Get the arguments from a collection type (e.g. ``typing.List[int]``) as a
    ``tuple``.
    :param t: the collection type.
    :return: a ``tuple`` containing types.
    """
    args_ = getattr(t, '__args__', tuple()) or tuple()
    args = tuple([attr for attr in args_
                  if type(attr) != typing.TypeVar])
    return args


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


def get_type(inst: T) -> typing.Type[T]:
    """
    Return a type, complete with generics for the given ``inst``.
    :param inst: the instance for which a type is to be returned.
    :return: the type of ``inst``.
    """
    result = type(inst)
    super_types = [
        (dict, _get_type_dict),
        (tuple, _get_type_tuple),
        (str, lambda inst_: result),
        (typing.Iterable, _get_type_iterable),
        (types.FunctionType, _get_type_callable),
        (types.MethodType, _get_type_callable),
        (type, lambda inst_: typing.Type[inst]),
    ]

    for super_type, func in super_types:
        if isinstance(inst, super_type):
            result = func(inst)
            break
    return result


def common_ancestor(*args: object) -> type:
    """
    Get the closest common ancestor of the given objects.
    :param args: any objects.
    :return: the ``type`` of the closest common ancestor of the given ``args``.
    """
    return _common_ancestor(args, False)


def common_ancestor_of_types(*args: type) -> type:
    """
    Get the closest common ancestor of the given classes.
    :param args: any classes.
    :return: the ``type`` of the closest common ancestor of the given ``args``.
    """
    return _common_ancestor(args, True)


def get_args_and_return_type(hint: typing.Type[typing.Callable]) \
        -> typing.Tuple[typing.Optional[typing.Tuple[type]], typing.Optional[type]]:
    """
    Get the argument types and the return type of a callable type hint
    (e.g. ``Callable[[int], str]).

    Example:
    ```
    arg_types, return_type = get_args_and_return_type(Callable[[int], str])
    # args_types is (int, )
    # return_type is str
    ```

    Example for when ``hint`` has no generics:
    ```
    arg_types, return_type = get_args_and_return_type(Callable)
    # args_types is None
    # return_type is None
    ```
    :param hint: the callable type hint.
    :return: a tuple of the argument types (as a tuple) and the return type.
    """
    if hint in (callable, typing.Callable):
        arg_types = None
        return_type = None
    elif hasattr(hint, '__result__'):
        arg_types = hint.__args__
        return_type = hint.__result__
    else:
        arg_types = hint.__args__[0:-1]
        return_type = hint.__args__[-1]
    return arg_types, return_type


def get_type_hints_of_callable(
        func: typing.Callable) -> typing.Dict[str, type]:
    """
    Return the type hints of the parameters of the given callable.
    :param func: the callable of which the type hints are to be returned.
    :return: a dict with parameter names and their types.
    """
    # Python3.5: get_type_hints raises on classes without explicit constructor
    try:
        result = typing.get_type_hints(func)
    except AttributeError:
        result = {}
    return result


def _subclass_of_generic(
        cls: type,
        info_generic_type: type,
        info_args: typing.Tuple[type, ...]) -> bool:
    # Check if cls is a subtype of info_generic_type, knowing that the latter
    # is a generic type.
    result = False
    cls_generic_type, cls_args = _split_generic(cls)
    if info_generic_type is tuple:
        # Special case.
        result = _subclass_of_tuple(cls_args, info_args)
    elif info_generic_type is typing.Union:
        # Another special case.
        result = _subclass_of_union(cls, info_args)
    elif (cls_generic_type == info_generic_type and cls_args
            and len(cls_args) == len(info_args)):
        for tup in zip(cls_args, info_args):
            if not subclass_of(*tup):
                result = False
                break
        else:
            result = True
    # Note that issubtype(list, List[...]) is always False.
    # Note that the number of arguments must be equal.
    return result


def _subclass_of_tuple(
        cls_args: typing.Tuple[type, ...],
        info_args: typing.Tuple[type, ...]) -> bool:
    result = False
    if len(info_args) == 2 and info_args[1] is ...:
        result = subclass_of(common_ancestor_of_types(*cls_args), info_args[0])
    elif len(cls_args) == len(info_args):
        for c1, c2 in zip(cls_args, info_args):
            if not subclass_of(c1, c2):
                break
        else:
            result = True
    return result


def _split_generic(t: type) -> \
        typing.Tuple[type, typing.Optional[typing.Tuple[type, ...]]]:
    # Split the given generic type into the type and its args.
    return get_origin(t), get_args(t)


def _get_type_iterable(inst: typing.Iterable):
    typing_type = get_alias(type(inst))
    common_cls = Unknown
    if inst:
        common_cls = common_ancestor(*inst)
        if typing_type:
            if issubclass(common_cls, typing.Iterable) and typing_type is not str:
                # Get to the bottom of it; obtain types recursively.
                common_cls = get_type(common_cls(_flatten(inst)))
    result = typing_type[common_cls]
    return result


def _get_type_tuple(inst: tuple) -> typing.Dict[KT, VT]:
    args = [get_type(elem) for elem in inst]
    return typing.Tuple[tuple(args)]


def _get_type_callable(
        inst: typing.Callable) -> typing.Type[typing.Dict[KT, VT]]:
    if 'lambda' in str(inst):
        result = _get_type_lambda(inst)
    else:
        result = typing.Callable
        sig = inspect.signature(inst)
        args = [_map_empty(param.annotation)
                for param in sig.parameters.values()]
        return_type = NoneType
        if sig.return_annotation != Empty:
            return_type = sig.return_annotation
        if args or return_type != NoneType:
            if inspect.iscoroutinefunction(inst):
                return_type = typing.Awaitable[return_type]
            result = typing.Callable[args, return_type]
    return result


def _map_empty(annotation: type) -> type:
    result = annotation
    if annotation == Empty:
        result = typing.Any
    return result


def _get_type_lambda(
        inst: typing.Callable) -> typing.Type[typing.Dict[KT, VT]]:
    args = [Unknown for _ in inspect.signature(inst).parameters]
    return_type = Unknown
    return typing.Callable[args, return_type]


def _get_type_dict(inst: typing.Dict[KT, VT]) -> typing.Type[typing.Dict[KT, VT]]:
    t_list_k = _get_type_iterable(list(inst.keys()))
    t_list_v = _get_type_iterable(list(inst.values()))
    _, t_k_tuple = _split_generic(t_list_k)
    _, t_v_tuple = _split_generic(t_list_v)
    return typing.Dict[t_k_tuple[0], t_v_tuple[0]]


def _flatten(l: typing.Iterable[typing.Iterable[typing.Any]]) -> typing.List[typing.Any]:
    result = []
    for x in l:
        result += [*x]
    return result


def _common_ancestor(args: typing.Sequence[object], types: bool) -> type:
    if len(args) < 1:
        raise TypeError('common_ancestor() requires at least 1 argument')

    mapper = (lambda x: x) if types else type
    mros = [getmro(mapper(elem)) for elem in args]
    for cls in mros[0]:
        for mro in mros:
            if cls not in mro:
                break
        else:
            # cls is in every mro; a common ancestor is found!
            return cls


def _subclass_of(cls: type, clsinfo: type) -> bool:
    clsinfo_origin, info_args = _split_generic(clsinfo)
    cls_origin = get_origin(cls)
    if cls is Unknown or clsinfo in (typing.Any, object):
        result = True
    elif cls is typing.Any:
        result = False
    elif cls_origin is typing.Union:
        _, cls_args = _split_generic(cls)
        result = _union_subclass_of(cls_args, clsinfo)
    elif info_args:
        result = _subclass_of_generic(cls, clsinfo_origin, info_args)
    else:
        try:
            result = issubclass(cls_origin, clsinfo_origin)
        except TypeError:
            result = False
    return result


def _union_subclass_of(
        cls_args: typing.Tuple[type, ...],
        clsinfo: type) -> bool:
    # Handle subclass_of(union, *)
    if sys.version_info[1] in (5, 6):
        raise TypeError('typish does not support Unions for Python versions '
                        'below 3.7')
    result = True
    for cls in cls_args:
        if subclass_of(cls, clsinfo):
            break
    else:
        result = False
    return result


def _subclass_of_union(
        cls: type,
        info_args: typing.Tuple[type, ...]) -> bool:
    # Handle subclass_of(*, union)
    result = True
    for cls_ in info_args:
        if subclass_of(cls, cls_):
            break
    else:
        result = False
    return result


@lru_cache()
def _get_simple_name(cls: type) -> str:
    if cls is None:
        cls = type(cls)
    cls_name = getattr(cls, '__name__', None)
    if not cls_name:
        cls_name = getattr(cls, '_name', None)
    if not cls_name:
        cls_name = repr(cls)
        cls_name = cls_name.split('[')[0]  # Remove generic types.
        cls_name = cls_name.split('.')[-1]  # Remove any . caused by repr.
        cls_name = cls_name.split(r"'>")[0]  # Remove any '>.
    return cls_name


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
}
