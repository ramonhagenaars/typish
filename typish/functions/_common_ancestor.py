import typing


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


def _common_ancestor(args: typing.Sequence[object], types: bool) -> type:
    from typish.functions._get_type import get_type
    from typish.functions._get_mro import get_mro

    if len(args) < 1:
        raise TypeError('common_ancestor() requires at least 1 argument')
    tmap = (lambda x: x) if types else get_type
    mros = [get_mro(tmap(elem)) for elem in args]
    for cls in mros[0]:
        for mro in mros:
            if cls not in mro:
                break
        else:
            # cls is in every mro; a common ancestor is found!
            return cls
