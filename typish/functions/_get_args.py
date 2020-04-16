import typing


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
