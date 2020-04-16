import inspect
from collections import OrderedDict
from typing import Callable, Any, Union, Iterable, Dict, Tuple

from typish._types import Empty
from typish.classes._cls_dict import ClsDict


class ClsFunction:
    """
    ClsDict is a callable that takes a ClsDict or a dict. When called, it uses
    the first argument to check for the right function in its body, executes it
    and returns the result.
    """
    def __init__(self, body: Union[ClsDict,
                                   Dict[type, Callable],
                                   Iterable[Tuple[type, Callable]],
                                   Iterable[Callable]]):
        from typish.functions._instance_of import instance_of

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
        elif instance_of(body, Iterable[Tuple[type, Callable]]):
            self.body = ClsDict(OrderedDict(body))
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
