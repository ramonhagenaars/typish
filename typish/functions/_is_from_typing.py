import typing


def is_from_typing(cls: type) -> bool:
    """
    Return True if the given class is from the typing module.
    :param cls: a type.
    :return: True if cls is from typing.
    """
    return cls.__module__ == typing.__name__
