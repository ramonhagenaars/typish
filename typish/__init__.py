import typing

import typish
from typish._classes import (
    SubscriptableType,
    Something,
    TypingType,
    ClsDict,
)
from typish._functions import (
    subclass_of,
    instance_of,
    get_origin,
    get_args,
    get_alias,
    get_type,
    common_ancestor,
    common_ancestor_of_types,
    get_args_and_return_type,
    get_type_hints_of_callable,
    is_type_annotation,
)
from typish._meta import (
    __version__,
)
from typish._types import (
    T,
    KT,
    VT,
    Empty,
    Unknown,
    Module,
    NoneType,
    Ellipsis_,
)

# As of Python 3.8, Literal is in the typing module.
Literal = getattr(typing, 'Literal', typish._classes.Literal)
