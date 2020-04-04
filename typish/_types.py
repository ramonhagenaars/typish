"""
PRIVATE MODULE: do not import (from) it directly.

This module contains types that are not available by default.
"""
import typing
from inspect import Parameter


T = typing.TypeVar('T')
KT = typing.TypeVar('KT')
VT = typing.TypeVar('VT')
Empty = Parameter.empty
Unknown = type('Unknown', (Empty, ), {})
Module = type(typing)
NoneType = type(None)
Ellipsis_ = type(...)  # Use EllipsisType instead.
EllipsisType = type(...)
