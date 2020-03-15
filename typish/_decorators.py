"""
PRIVATE MODULE: do not import (from) it directly.

This module contains decorators.
"""
import inspect

from typish._functions import _map_empty, instance_of


def typechecked(decorated):

    sig = inspect.signature(decorated)
    param_names = list(sig.parameters)

    def _wrapper(*args, **kwargs):
        for i, arg in enumerate(args):
            param = sig.parameters[param_names[i]]
            param_type = _map_empty(param.annotation)
            if not instance_of(arg, param_type):
                raise TypeError('Value {} for \'{}\' is not of type \'{}\''
                                .format(arg, param.name, param_type))
        return decorated(*args, **kwargs)

    return _wrapper
