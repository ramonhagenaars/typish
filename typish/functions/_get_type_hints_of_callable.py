import typing


def get_type_hints_of_callable(
        func: typing.Callable) -> typing.Dict[str, type]:
    """
    Return the type hints of the parameters of the given callable.
    :param func: the callable of which the type hints are to be returned.
    :return: a dict with parameter names and their types.
    """
    # Python3.5: get_type_hints raises on classes without explicit constructor
    try:
        result = typing.get_type_hints(func)
    except AttributeError:
        result = {}
    return result


def get_args_and_return_type(hint: typing.Type[typing.Callable]) \
        -> typing.Tuple[typing.Optional[typing.Tuple[type]], typing.Optional[type]]:
    """
    Get the argument types and the return type of a callable type hint
    (e.g. ``Callable[[int], str]``).

    Example:
    ```
    arg_types, return_type = get_args_and_return_type(Callable[[int], str])
    # args_types is (int, )
    # return_type is str
    ```

    Example for when ``hint`` has no generics:
    ```
    arg_types, return_type = get_args_and_return_type(Callable)
    # args_types is None
    # return_type is None
    ```
    :param hint: the callable type hint.
    :return: a tuple of the argument types (as a tuple) and the return type.
    """
    if hint in (callable, typing.Callable):
        arg_types = None
        return_type = None
    elif hasattr(hint, '__result__'):
        arg_types = hint.__args__
        return_type = hint.__result__
    else:
        arg_types = hint.__args__[0:-1]
        return_type = hint.__args__[-1]
    return arg_types, return_type
