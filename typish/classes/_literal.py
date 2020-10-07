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
                result = SubscriptableType.__getattribute__(cls, item)
                if (result and isinstance(result, tuple)
                        and isinstance(result[0], tuple)):
                    result = result[0]  # result was a tuple in a tuple.
                if result and not isinstance(result, tuple):
                    result = (result,)
            except AttributeError:  # pragma: no cover
                # In case of Python 3.5
                result = tuple()
        elif item in ('__origin__', '__name__', '_name'):
            result = 'Literal'
        else:
            result = SubscriptableType.__getattribute__(cls, item)
        return result

    def __instancecheck__(self, instance):
        return self.__args__ and instance in self.__args__

    def __str__(self):
        args = ', '.join(str(arg) for arg in self.__args__)
        return '{}[{}]'.format(self.__name__, args)

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
        return LiteralAlias[args] if args else LiteralAlias


# If Literal is available (Python 3.8+), then return that type instead.
Literal = getattr(typing, 'Literal', LiteralAlias)
