import typing

from typish._types import Unknown


def subclass_of(cls: type, *args: type) -> bool:
    """
    Return whether ``cls`` is a subclass of all types in ``args`` while also
    considering generics.
    :param cls: the subject.
    :param args: the super types.
    :return: True if ``cls`` is a subclass of all types in ``args`` while also
    considering generics.
    """
    from typish.classes._literal import LiteralAlias

    if args and issubclass(args[0], LiteralAlias):
        return _check_literal(cls, subclass_of, *args)

    if len(args) > 1:
        result = subclass_of(cls, args[0]) and subclass_of(cls, *args[1:])
    else:
        if args[0] == cls:
            return True
        result = _subclass_of(cls, args[0])
    return result


def _subclass_of(cls: type, clsinfo: type) -> bool:
    from typish.functions._get_origin import get_origin
    from typish.functions._get_args import get_args

    # Check whether cls is a subtype of clsinfo.
    clsinfo_origin = get_origin(clsinfo)
    clsinfo_args = get_args(clsinfo)
    cls_origin = get_origin(cls)
    if cls is Unknown or clsinfo in (typing.Any, object):
        result = True
    elif cls_origin is typing.Union:
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
    elif cls_origin is tuple and info_generic_type is typing.Iterable:
        # Another special case.
        args = cls_args
        if len(args) > 1 and args[1] is ...:
            args = [args[0]]

        # Match the number of arguments of info to that of cls.
        matched_info_args = info_args * len(args)
        result = _subclass_of_tuple(args, matched_info_args)
    elif info_generic_type is typing.Union:
        # Another special case.
        result = _subclass_of_union(cls, info_args)
    elif (subclass_of(cls_origin, info_generic_type) and cls_args
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
        for c1, c2 in zip(cls_args, info_args):
            if not subclass_of(c1, c2):
                break
        else:
            result = True
    return result


def _check_literal(obj: object, func: typing.Callable, *args: type) -> bool:
    # Instance or subclass check for Literal.
    literal = args[0]
    leftovers = args[1:]
    literal_args = getattr(literal, '__args__', None)
    if literal_args:
        literal_arg = literal_args[0]
        return obj == literal_arg and (not leftovers or func(obj, *leftovers))
    return False
