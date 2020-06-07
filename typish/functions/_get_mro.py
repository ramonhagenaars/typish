import typing
from inspect import getmro


def get_mro(obj: typing.Any) -> typing.Tuple[type, ...]:
    """
    Return tuple of base classes (including that of obj) in method resolution
    order. Types from typing are supported as well.
    :param obj: object or type.
    :return: a tuple of base classes.
    """
    from typish.functions._get_origin import get_origin

    # Wrapper around ``getmro`` to allow types from ``typing``.
    if obj is ...:
        return Ellipsis, object
    elif obj is typing.Union:
        # For Python <3.7, we cannot use mro.
        super_cls = getattr(typing, '_GenericAlias',
                            getattr(typing, 'GenericMeta', None))
        return typing.Union, super_cls, object

    origin = get_origin(obj)
    if origin != obj:
        return get_mro(origin)

    cls = obj
    if not isinstance(obj, type):
        cls = type(obj)

    return getmro(cls)
