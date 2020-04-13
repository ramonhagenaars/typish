import typing
from inspect import getmro


def get_mro(cls: type) -> typing.Tuple[type, ...]:
    from typish.functions._get_origin import get_origin

    # Wrapper around ``getmro`` to allow types from ``Typing``.
    if cls is ...:
        return Ellipsis, object
    elif cls is typing.Union:
        # For Python <3.7, we cannot use mro.
        super_cls = getattr(typing, '_GenericAlias',
                            getattr(typing, 'GenericMeta', None))
        return (typing.Union, super_cls, object)

    origin = get_origin(cls)
    if origin != cls:
        return get_mro(origin)

    return getmro(cls)
