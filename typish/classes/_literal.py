import typing

from typish.classes._subscriptable_type import SubscriptableType


def is_literal_type(cls: typing.Any) -> bool:
    """
    Return whether cls is a Literal type.
    :param cls: the type that is to be checked.
    :return: True if cls is a Literal type.
    """
    from typish.functions._get_simple_name import get_simple_name

    return get_simple_name(cls) == 'Literal'


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

    def __str__(self):
        return '{}[{}]'.format(self.__name__, self.__args__[0])

    def __subclasscheck__(self, subclass: typing.Any) -> bool:
        return is_literal_type(subclass)


class LiteralAlias(type, metaclass=_LiteralMeta):
    """
    This is a backwards compatible variant of typing.Literal (Python 3.8+).
    """
    @staticmethod
    def from_literal(literal: typing.Any) -> typing.Type['LiteralAlias']:
        """
        Create a LiteralAlias from the given typing.Literal.
        :param literal: the typing.Literal type.
        :return: a LiteralAlias type.
        """
        from typish.functions._get_args import get_args

        args = get_args(literal)
        return LiteralAlias[args[0]] if args else LiteralAlias


# If Literal is available (Python 3.8+), then return that type instead.
Literal = getattr(typing, 'Literal', LiteralAlias)
