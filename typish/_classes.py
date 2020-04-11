"""
PRIVATE MODULE: do not import (from) it directly.

This module contains class implementations.
"""
import inspect
import types
from collections import OrderedDict
from typing import Any, Callable, Dict, Tuple, Optional, Union, List, Iterable

from typish._types import Empty
from typish._functions import (
    get_type,
    subclass_of,
    instance_of,
    get_args_and_return_type,
    is_type_annotation,
)


class _SubscribedType(type):
    """
    This class is a placeholder to let the IDE know the attributes of the
    returned type after a __getitem__.
    """
    __origin__ = None
    __args__ = None


class SubscriptableType(type):
    """
    This metaclass will allow a type to become subscriptable.

    >>> class SomeType(metaclass=SubscriptableType):
    ...     pass
    >>> SomeTypeSub = SomeType['some args']
    >>> SomeTypeSub.__args__
    'some args'
    >>> SomeTypeSub.__origin__.__name__
    'SomeType'
    """
    def __init_subclass__(mcs, **kwargs):
        mcs._hash = None
        mcs.__args__ = None
        mcs.__origin__ = None

    def __getitem__(self, item) -> _SubscribedType:
        body = {
            **self.__dict__,
            '__args__': item,
            '__origin__': self,
        }
        bases = self, *self.__bases__
        result = type(self.__name__, bases, body)
        if hasattr(result, '_after_subscription'):
            # TODO check if _after_subscription is static
            result._after_subscription(item)
        return result

    def __eq__(self, other):
        self_args = getattr(self, '__args__', None)
        self_origin = getattr(self, '__origin__', None)
        other_args = getattr(other, '__args__', None)
        other_origin = getattr(other, '__origin__', None)
        return self_args == other_args and self_origin == other_origin

    def __hash__(self):
        if not getattr(self, '_hash', None):
            self._hash = hash('{}{}'.format(self.__origin__, self.__args__))
        return self._hash


class _SomethingMeta(SubscriptableType):
    """
    This metaclass is coupled to ``Interface``.
    """
    def __instancecheck__(self, instance: object) -> bool:
        # Check if all attributes from self.signature are also present in
        # instance and also check that their types correspond.
        sig = self.signature()
        for key in sig:
            attr = getattr(instance, key, None)
            if not attr or not instance_of(attr, sig[key]):
                return False
        return True

    def __subclasscheck__(self, subclass: type) -> bool:
        # If an instance of type subclass is an instance of self, then subclass
        # is a sub class of self.
        self_sig = self.signature()
        other_sig = Something.like(subclass).signature()
        for attr in self_sig:
            if attr in other_sig:
                attr_sig = other_sig[attr]
                if (not isinstance(subclass.__dict__[attr], staticmethod)
                        and not isinstance(subclass.__dict__[attr], classmethod)
                        and subclass_of(attr_sig, Callable)):
                    # The attr must be a regular method or class method, so the
                    # first parameter should be ignored.
                    args, rt = get_args_and_return_type(attr_sig)
                    attr_sig = Callable[list(args[1:]), rt]
                if not subclass_of(attr_sig, self_sig[attr]):
                    return False
        return True

    def __eq__(self, other: 'Something') -> bool:
        return (isinstance(other, _SomethingMeta)
                and self.signature() == other.signature())

    def __repr__(self):
        sig = self.signature()
        sig_ = ', '.join(["'{}': {}".format(k, self._type_repr(sig[k]))
                          for k in sig])
        return 'typish.Something[{}]'.format(sig_)

    def __hash__(self):
        # This explicit super call is required for Python 3.5 and 3.6.
        return super.__hash__(self)

    def _type_repr(self, obj):
        """Return the repr() of an object, special-casing types (internal helper).

        If obj is a type, we return a shorter version than the default
        type.__repr__, based on the module and qualified name, which is
        typically enough to uniquely identify a type.  For everything
        else, we fall back on repr(obj).
        """
        if isinstance(obj, type) and not issubclass(obj, Callable):
            if obj.__module__ == 'builtins':
                return obj.__qualname__
            return '{}.{}'.format(obj.__module__, obj.__qualname__)
        if obj is ...:
            return '...'
        if isinstance(obj, types.FunctionType):
            return obj.__name__
        return repr(obj)


class Something(type, metaclass=_SomethingMeta):
    """
    This class allows one to define an interface for something that has some
    attributes, such as objects or classes or maybe even modules.
    """
    @classmethod
    def signature(mcs) -> Dict[str, type]:
        """
        Return the signature of this ``Something`` as a dict.
        :return: a dict with attribute names as keys and types as values.
        """
        result = OrderedDict()
        args = mcs.__args__
        if isinstance(mcs.__args__, slice):
            args = (mcs.__args__,)

        arg_keys = sorted(args)
        if isinstance(mcs.__args__, dict):
            for key in arg_keys:
                result[key] = mcs.__args__[key]
        else:
            for slice_ in arg_keys:
                result[slice_.start] = slice_.stop
        return result

    def __getattr__(cls, item):
        # This method exists solely to fool the IDE into believing that
        # Something can have any attribute.
        return type.__getattr__(cls, item)

    @staticmethod
    def like(obj: Any, exclude_privates: bool = True) -> 'Something':
        """
        Return a ``Something`` for the given ``obj``.
        :param obj: the object of which a ``Something`` is to be made.
        :param exclude_privates: if ``True``, private variables are excluded.
        :return: a ``Something`` that corresponds to ``obj``.
        """
        signature = {attr: get_type(getattr(obj, attr)) for attr in dir(obj)
                     if not exclude_privates or not attr.startswith('_')}
        return Something[signature]


class ClsDict(OrderedDict):
    """
    ClsDict is a dict that accepts (only) types as keys and will return its
    values depending on instance checks rather than equality checks.
    """
    def __new__(cls, *args, **kwargs):
        """
        Construct a new instance of ``ClsDict``.
        :param args: a dict.
        :param kwargs: any kwargs that ``dict`` accepts.
        :return: a ``ClsDict``.
        """
        if len(args) > 1:
            raise TypeError('TypeDict accepts only one positional argument, '
                            'which must be a dict.')
        if args and not isinstance(args[0], dict):
            raise TypeError('TypeDict accepts only a dict as positional '
                            'argument.')
        if not all([is_type_annotation(key) for key in args[0]]):
            raise TypeError('The given dict must only hold types as keys.')
        return super().__new__(cls, args[0], **kwargs)

    def __getitem__(self, item: Any) -> Any:
        """
        Return the value of the first encounter of a key for which
        ``is_instance(item, key)`` holds ``True``.
        :param item: any item.
        :return: the value of which the type corresponds with item.
        """
        item_type = get_type(item, use_union=True)
        for key, value in self.items():
            if subclass_of(item_type, key):
                return value
        raise KeyError('No match for {}'.format(item))

    def get(self, item: Any, default: Any = None) -> Optional[Any]:
        try:
            return self.__getitem__(item)
        except KeyError:
            return default


class ClsFunction:
    """
    ClsDict is a callable that takes a ClsDict or a dict. When called, it uses
    the first argument to check for the right function in its body, executes it
    and returns the result.
    """
    def __init__(self, body: Union[ClsDict, dict, Iterable[Callable]]):
        if isinstance(body, ClsDict):
            self.body = body
        elif isinstance(body, dict):
            self.body = ClsDict(body)
        elif instance_of(body, Iterable[Callable]):
            list_of_tuples = []
            for func in body:
                signature = inspect.signature(func)
                params = list(signature.parameters.keys())
                if not params:
                    raise TypeError('ClsFunction expects callables that take '
                                    'at least one parameter, {} does not.'
                                    .format(func.__name__))
                first_param = signature.parameters[params[0]]
                hint = first_param.annotation
                key = Any if hint == Empty else hint
                list_of_tuples.append((key, func))
            self.body = ClsDict(OrderedDict(list_of_tuples))
        else:
            raise TypeError('ClsFunction expects a ClsDict or a dict that can '
                            'be turned to a ClsDict or an iterable of '
                            'callables.')

        if not all(isinstance(value, Callable) for value in self.body.values()):
            raise TypeError('ClsFunction expects a dict or ClsDict with only '
                            'callables as values.')

    def understands(self, item: Any) -> bool:
        """
        Check to see if this ClsFunction can take item.
        :param item: the item that is checked.
        :return: True if this ClsFunction can take item.
        """
        try:
            self.body[item]
            return True
        except KeyError:
            return False

    def __call__(self, *args, **kwargs):
        if not args:
            raise TypeError('ClsFunction must be called with at least 1 '
                            'positional argument.')
        callable_ = self.body[args[0]]
        try:
            return callable_(*args, **kwargs)
        except TypeError as err:
            raise TypeError('Unable to call function for \'{}\': {}'
                            .format(args[0], err.args[0]))


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
        elif item == '__origin__':
            result = 'Literal'
        else:
            result = SubscriptableType.__getattribute__(cls, item)
        return result

    def __instancecheck__(self, instance):
        return self.__args__ and self.__args__[0] == instance


class Literal(metaclass=_LiteralMeta):
    """
    This is a backwards compatible variant of typing.Literal (Python 3.8+).
    """
    _name = 'Literal'


TypingType = Something['__origin__': type, '__args__': Tuple[type, ...]]
