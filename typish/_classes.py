"""
PRIVATE MODULE: do not import (from) it directly.

This module contains class implementations.
"""
from typing import Type, Dict, Tuple, Any
from typish import get_type
from typish._functions import instance_of


class _InterfaceMeta(type):
    signature = None

    def __getitem__(self,
                    cls_signature: Dict[str, type]) -> Type['Interface']:
        return Interface(cls_signature=cls_signature, suppress_error=True)

    def __instancecheck__(self, instance: object) -> bool:
        # Check if all attributes from self.signature are also present in
        # instance and also check that their types correspond.
        for key in self.signature:
            attr = getattr(instance, key, None)
            if not attr or not instance_of(attr, self.signature[key]):
                return False
        return True

    def __repr__(self):
        return 'Interface[{}]'.format(self.signature)


class Interface(type, metaclass=_InterfaceMeta):
    """
    The ``Interface`` can be used to denote any type that contains attributes,
    such as classes or instances.

    For example, to denote a type what has an attribute of type ``int``, you'll
    write:

        ``Interface[{'some_attr': int}]``

    You can also define functions:

        ``Interface[{'some_attr': int, 'some_func': Callable[[int], str]}]``

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
