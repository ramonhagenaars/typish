from typish._state import DEFAULT, State


def instance_of(obj: object, *args: object, state: State = DEFAULT) -> bool:
    """
    Check whether ``obj`` is an instance of all types in ``args``, while also
    considering generics.

    If you want the instance check to be customized for your type, then make
    sure it has a __instancecheck__ defined (not in a base class). You will
    also need to register the get_type function by calling
    typish.register_get_type with that particular type and a handling callable.
    :param obj: the object in subject.
    :param args: the type(s) of which ``obj`` is an instance or not.
    :param state: any state that is used by typish.
    :return: ``True`` if ``obj`` is an instance of all types in ``args``.
    """
    return all(_instance_of(obj, clsinfo, state) for clsinfo in args)


def _instance_of(obj: object, clsinfo: object, state: State = DEFAULT) -> bool:
    from typish.classes._literal import LiteralAlias, is_literal_type
    from typish.functions._subclass_of import subclass_of
    from typish.functions._get_type import get_type
    from typish.functions._is_from_typing import is_from_typing

    if not is_from_typing(clsinfo) and '__instancecheck__' in dir(clsinfo):
        return isinstance(obj, clsinfo)

    if is_literal_type(clsinfo):
        alias = LiteralAlias.from_literal(clsinfo)
        return isinstance(obj, alias)

    type_ = get_type(obj, use_union=True, state=state)
    return subclass_of(type_, clsinfo)
