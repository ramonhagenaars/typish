import typing

from typish._types import Unknown
from typish.functions._get_alias import get_alias


def subclass_of(cls: object, *args: object) -> bool:
    """
    Return whether ``cls`` is a subclass of all types in ``args`` while also
    considering generics.

    If you want the subclass check to be customized for your type, then make
    sure it has a __subclasscheck__ defined (not in a base class).
    :param cls: the subject.
    :param args: the super types.
    :return: True if ``cls`` is a subclass of all types in ``args`` while also
    considering generics.
    """
    return all(_subclass_of(cls, clsinfo) for clsinfo in args)


def _subclass_of(cls: type, clsinfo: object) -> bool:
    # Check whether cls is a subtype of clsinfo.
    from typish.classes._literal import LiteralAlias

    # Translate to typing type if possible.
    clsinfo = get_alias(clsinfo) or clsinfo

    if _is_true_case(cls, clsinfo):
        result = True
    elif issubclass(clsinfo, LiteralAlias):
        return _check_literal(cls, subclass_of, clsinfo)
    elif is_issubclass_case(cls, clsinfo):
        result = issubclass(cls, clsinfo)
    else:
        result = _forward_subclass_check(cls, clsinfo)

    return result


def _forward_subclass_check(cls: type, clsinfo: type) -> bool:
    # Forward the subclass check for cls and clsinfo to delegates that know how
    # to check that particular cls/clsinfo type.

    from typish.functions._get_origin import get_origin
    from typish.functions._get_args import get_args

    clsinfo_origin = get_origin(clsinfo)
    clsinfo_args = get_args(clsinfo)
    cls_origin = get_origin(cls)

    if cls_origin is typing.Union:
        # cls is a Union; all options of that Union must subclass clsinfo.
        cls_args = get_args(cls)
        result = all([subclass_of(elem, clsinfo) for elem in cls_args])
    elif clsinfo_args:
        result = _subclass_of_generic(cls, clsinfo_origin, clsinfo_args)
    else:
        try:
            result = issubclass(cls_origin, clsinfo_origin)
        except TypeError:
            result = False
    return result


def _subclass_of_generic(
        cls: type,
        info_generic_type: type,
        info_args: typing.Tuple[type, ...]) -> bool:
    # Check if cls is a subtype of info_generic_type, knowing that the latter
    # is a generic type.

    from typish.functions._get_origin import get_origin
    from typish.functions._get_args import get_args

    result = False
    cls_origin = get_origin(cls)
    cls_args = get_args(cls)
    if info_generic_type is tuple:
        # Special case.
        result = (subclass_of(cls_origin, tuple)
                  and _subclass_of_tuple(cls_args, info_args))
    elif info_generic_type is typing.Union:
        # Another special case.
        result = any(subclass_of(cls, cls_) for cls_ in info_args)
    elif cls_origin is tuple and info_generic_type is typing.Iterable:
        # Another special case.
        args = _tuple_args(cls_args)

        # Match the number of arguments of info to that of cls.
        matched_info_args = info_args * len(args)
        result = _subclass_of_tuple(args, matched_info_args)
    elif (subclass_of(cls_origin, info_generic_type) and cls_args
          and len(cls_args) == len(info_args)):
        result = all(subclass_of(*tup) for tup in zip(cls_args, info_args))
    # Note that issubtype(list, List[...]) is always False.
    # Note that the number of arguments must be equal.
    return result


def _subclass_of_tuple(
        cls_args: typing.Tuple[type, ...],
        info_args: typing.Tuple[type, ...]) -> bool:
    from typish.functions._get_origin import get_origin
    from typish.functions._common_ancestor import common_ancestor_of_types

    result = False
    if len(info_args) == 2 and info_args[1] is ...:
        type_ = get_origin(info_args[0])
        if type_ is typing.Union:
            # A heterogeneous tuple: check each element if it subclasses the
            # union.
            result = all([subclass_of(elem, info_args[0]) for elem in cls_args])
        else:
            result = subclass_of(common_ancestor_of_types(*cls_args), info_args[0])
    elif len(cls_args) == len(info_args):
        result = all(subclass_of(c1, c2)
                     for c1, c2 in zip(cls_args, info_args))
    return result


def _check_literal(obj: object, func: typing.Callable, *args: type) -> bool:
    # Instance or subclass check for Literal.
    literal = args[0]
    leftovers = args[1:]
    literal_args = getattr(literal, '__args__', None)
    result = False
    if literal_args:
        literal_arg = literal_args[0]
        result = (obj == literal_arg
                  and (not leftovers or func(obj, *leftovers)))
    return result


def _is_true_case(cls: type, clsinfo: type) -> bool:
    # Return whether subclass_of(cls, clsinfo) holds a case that must always be
    # True, without the need of further checking.
    return cls == clsinfo or cls is Unknown or clsinfo in (typing.Any, object)


def is_issubclass_case(cls: type, clsinfo: type) -> bool:
    # Return whether subclass_of(cls, clsinfo) holds a case that can be handled
    # by the builtin issubclass.
    from typish.functions._is_from_typing import is_from_typing

    return (not is_from_typing(clsinfo)
            and isinstance(cls, type)
            and clsinfo is not type
            and '__subclasscheck__' in dir(clsinfo))


def _tuple_args(
        cls_args: typing.Iterable[typing.Any]) -> typing.Iterable[type]:
    # Get the argument types from a tuple, even if the form is Tuple[int, ...].
    result = cls_args
    if len(cls_args) > 1 and cls_args[1] is ...:
        result = [cls_args[0]]
    return result
