import typing

from typish.classes._union_type import UnionType


def is_type_annotation(item: typing.Any) -> bool:
    """
    Return whether item is a type annotation (a ``type`` or a type from
    ``typing``, such as ``List``).
    :param item: the item in question.
    :return: ``True`` is ``item`` is a type annotation.
    """
    from typish.functions._instance_of import instance_of

    # Use _GenericAlias for Python 3.7+ and use GenericMeta for the rest.
    super_cls = getattr(typing, '_GenericAlias',
                        getattr(typing, 'GenericMeta', None))

    return not isinstance(item, typing.TypeVar) and (
            item is typing.Any
            or instance_of(item, type)
            or instance_of(item, super_cls)
            or getattr(item, '__module__', None) == 'typing'
            or isinstance(item, UnionType))
