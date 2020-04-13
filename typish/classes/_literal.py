import typing

from typish.classes._subscriptable_type import SubscriptableType


class _LiteralMeta(SubscriptableType):
    """
    A Metaclass that exists to serve Literal and alter the __args__ attribute.
    """
    def __getattribute__(cls, item):
        """
        This method makes sure that __args__ is a tuple, like with
        typing.Literal.
        :param item: the name of the attribute that is obtained.
        :return: the attribute.
        """
        if item == '__args__':
            try:
                result = SubscriptableType.__getattribute__(cls, item),
            except AttributeError:
                # In case of Python 3.5
                result = tuple()
        elif item in ('__origin__', '__name__', '_name'):
            result = 'Literal'
        else:
            result = SubscriptableType.__getattribute__(cls, item)
        return result

    def __instancecheck__(self, instance):
        return self.__args__ and self.__args__[0] == instance

    def __subclasscheck__(self, subclass: typing.Any) -> bool:
        from typish.functions._get_simple_name import get_simple_name

        return get_simple_name(subclass) == 'Literal'


class LiteralAlias(type, metaclass=_LiteralMeta):
    """
    This is a backwards compatible variant of typing.Literal (Python 3.8+).
    """


# If Literal is available (Python 3.8+), then return that type instead.
Literal = getattr(typing, 'Literal', LiteralAlias)
