from functools import lru_cache

from typish._types import NoneType


@lru_cache()
def get_simple_name(cls: type) -> str:
    cls = cls or NoneType
    cls_name = getattr(cls, '__name__', None)
    if not cls_name:
        cls_name = getattr(cls, '_name', None)
    if not cls_name:
        cls_name = repr(cls)
        cls_name = cls_name.split('[')[0]  # Remove generic types.
        cls_name = cls_name.split('.')[-1]  # Remove any . caused by repr.
        cls_name = cls_name.split(r"'>")[0]  # Remove any '>.
    return cls_name
