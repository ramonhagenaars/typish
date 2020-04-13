def instance_of(obj: object, *args: type) -> bool:
    """
    Check whether ``obj`` is an instance of all types in ``args``, while also
    considering generics.
    :param obj: the object in subject.
    :param args: the type(s) of which ``obj`` is an instance or not.
    :return: ``True`` if ``obj`` is an instance of all types in ``args``.
    """
    from typish.classes._literal import Literal, LiteralAlias
    from typish.functions._subclass_of import subclass_of
    from typish.functions._get_type import get_type

    try:
        return all(isinstance(obj, arg) for arg in args)
    except Exception:
        ...  # If the regular check didn't work, continue below.

    if args and issubclass(args[0], Literal):
        leftovers = args[1:]
        return (LiteralAlias.__instancecheck__(args[0], obj)
                and (not leftovers or instance_of(obj, leftovers)))

    type_ = get_type(obj, use_union=True)
    return subclass_of(type_, *args)
