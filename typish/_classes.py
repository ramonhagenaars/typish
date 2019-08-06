"""
PRIVATE MODULE: do not import (from) it directly.

This module contains class implementations.
"""
from typing import Type, Dict, Tuple, Any, Callable, Union
from typish._functions import (
    get_type,
    subclass_of,
    instance_of,
    get_args_and_return_type,
)


class _InterfaceMeta(type):
    signature = {}

    def __getitem__(
            self,
            cls_signature: Union[Dict[str, type], Tuple[slice, ...]]
    ) -> Type['Interface']:
        if not isinstance(cls_signature, dict):
            cls_signature = {slice_.start: slice_.stop
                             for slice_ in cls_signature}
        return Interface(cls_signature=cls_signature, suppress_error=True)

    @property
    def __args__(cls):
        return cls.signature

    def __instancecheck__(self, instance: object) -> bool:
        # Check if all attributes from self.signature are also present in
        # instance and also check that their types correspond.
        for key in self.signature:
            attr = getattr(instance, key, None)
            if not attr or not instance_of(attr, self.signature[key]):
                return False
        return True

    def __subclasscheck__(self, subclass: type) -> bool:
        # If an instance of type subclass is an instance of self, then subclass
        # is a sub class of self.
        self_sig = self.signature
        other_sig = Interface.of(subclass).signature
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

    def __eq__(self, other: 'Interface') -> bool:
        return (isinstance(other, Interface)
                and self.signature == other.signature)

    def __repr__(self):
        return 'Interface[{}]'.format(self.signature)


class Interface(type, metaclass=_InterfaceMeta):
    """
    The ``Interface`` can be used to denote any type that contains attributes,
    such as classes or instances.

    For example, to denote a type what has an attribute of type ``int``, you'll
    write:

        ``Interface['some_attr': int]``

    You can also define functions:

        ``Interface['some_attr': int, 'some_func': Callable[[int], str]]``

    The ``Interface`` instances can be used with ``instanceof`` to check
    whether some type adheres to that interface.
    """
    def __new__(mcs, cls_signature: Dict[str, type],
                **kwargs) -> Type['Interface']:
        if 'suppress_error' not in kwargs:
            raise TypeError('Type {} cannot be instantiated'
                            .format(mcs.__name__))
        cls_content = {
            'signature': cls_signature
        }
        return type('Interface', (Interface, ), cls_content)

    @staticmethod
    def of(obj: Any, exclude_privates: bool = True) -> 'Interface':
        """
        Return an ``Interface`` for the given ``obj``.
        :param obj: the object of which an ``Interface`` is to be made.
        :param exclude_privates: if ``True``, private variables are excluded.
        :return: an ``Interface`` that corresponds to ``obj``.
        """
        signature = {attr: get_type(getattr(obj, attr)) for attr in dir(obj)
                     if not exclude_privates or not attr.startswith('_')}
        return Interface[signature]


GenericCollection = Interface[{'__origin__': type, '__args__': Tuple[type]}]
