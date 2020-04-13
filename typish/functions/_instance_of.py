import typing


def instance_of(obj: object, *args: type) -> bool:
    """
    Check whether ``obj`` is an instance of all types in ``args``, while also
    considering generics.
    :param obj: the object in subject.
    :param args: the type(s) of which ``obj`` is an instance or not.
    :return: ``True`` if ``obj`` is an instance of all types in ``args``.
    """
    from typish.classes._literal import Literal
    from typish.functions._subclass_of import subclass_of
    from typish.functions._get_type import get_type

    try:
        return all(isinstance(obj, arg) for arg in args)
    except Exception:
        ...  # If the regular check didn't work, continue below.

    if args and issubclass(args[0], Literal):
        return _check_literal(obj, instance_of, *args)

    type_ = get_type(obj, use_union=True)
    return subclass_of(type_, *args)


def _check_literal(obj: object, func: typing.Callable, *args: type) -> bool:  # TODO refactor
    # Instance or subclass check for Literal.
    literal = args[0]
    leftovers = args[1:]
    literal_args = getattr(literal, '__args__', None)
    if literal_args:
        literal_arg = literal_args[0]
        return obj == literal_arg and (not leftovers or func(obj, *leftovers))
    return False
