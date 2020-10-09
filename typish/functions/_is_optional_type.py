import typing

from typish import get_origin, get_args, NoneType


def is_optional_type(cls: type) -> bool:
    """
    Return True if the given class is an optional type. A type is considered to
    be optional if it allows ``None`` as value.

    Example:

    is_optional_type(Optional[str])  # True
    is_optional_type(Union[str, int, None])  # True
    is_optional_type(str)  # False
    is_optional_type(Union[str, int])  # False

    :param cls: a type.
    :return: True if cls is an optional type.
    """
    origin = get_origin(cls)
    args = get_args(cls)
    return origin == typing.Union and NoneType in args
