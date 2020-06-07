from typing import Callable

from typish import T


class State:
    """
    A class which instances hold any state that may be used by typish.
    """
    def __init__(self) -> None:
        """
        Constructor.
        """
        self.get_type_per_cls = {}

    def register_get_type(
            self,
            cls: T,
            get_type_function: Callable[[T], type]) -> None:
        """
        Register a callable for some type that is to be used when calling
        typish.get_type.
        :param cls: the type for which that given callable is to be called.
        :param get_type_function: the callable to call for that type.
        :return: None.
        """
        self.get_type_per_cls[cls] = get_type_function


DEFAULT = State()


def register_get_type(
        cls: T,
        get_type_function: Callable[[T], type],
        state: State = DEFAULT) -> None:
    """
    Register a callable for some type that is to be used when calling
    typish.get_type.
    :param cls: the type for which that given callable is to be called.
    :param get_type_function: the callable to call for that type.
    :param state: any state that is used by typish.
    :return: None.
    """
    state.register_get_type(cls, get_type_function)
