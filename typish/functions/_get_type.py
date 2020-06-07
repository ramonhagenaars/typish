import inspect
import types
import typing

from typish._state import DEFAULT, State
from typish._types import T, Unknown, KT, NoneType, Empty, VT
from typish.classes._union_type import UnionType


def get_type(
        inst: T,
        use_union: bool = False,
        *,
        state: State = DEFAULT) -> typing.Type[T]:
    """
    Return a type, complete with generics for the given ``inst``.
    :param inst: the instance for which a type is to be returned.
    :param use_union: if ``True``, the resulting type can contain a union.
    :param state: any state that is used by typish.
    :return: the type of ``inst``.
    """

    get_type_for_inst = state.get_type_per_cls.get(type(inst))
    if get_type_for_inst:
        return get_type_for_inst(inst)

    if inst is typing.Any:
        return typing.Any

    if isinstance(inst, UnionType):
        return UnionType

    result = type(inst)
    super_types = [
        (dict, _get_type_dict),
        (tuple, _get_type_tuple),
        (str, lambda inst_, _, __: result),
        (typing.Iterable, _get_type_iterable),
        (types.FunctionType, _get_type_callable),
        (types.MethodType, _get_type_callable),
        (type, lambda inst_, _, __: typing.Type[inst]),
    ]

    try:
        for super_type, func in super_types:
            if isinstance(inst, super_type):
                result = func(inst, use_union, state)
                break
    except Exception:
        # If anything went wrong, return the regular type.
        # This is to support 3rd party libraries.
        return type(inst)
    return result


def _get_type_iterable(
        inst: typing.Iterable,
        use_union: bool,
        state: State) -> type:
    from typish.functions._get_alias import get_alias
    from typish.functions._common_ancestor import common_ancestor

    typing_type = get_alias(type(inst))
    common_cls = Unknown
    if inst:
        if use_union:
            types = [get_type(elem, state=state) for elem in inst]
            common_cls = typing.Union[tuple(types)]
        else:
            common_cls = common_ancestor(*inst)
            if typing_type:
                if issubclass(common_cls, typing.Iterable) and typing_type is not str:
                    # Get to the bottom of it; obtain types recursively.
                    common_cls = get_type(common_cls(_flatten(inst)), state=state)
    result = typing_type[common_cls]
    return result


def _get_type_tuple(
        inst: tuple,
        use_union: bool,
        state: State) -> typing.Dict[KT, VT]:
    args = [get_type(elem, state) for elem in inst]
    return typing.Tuple[tuple(args)]


def _get_type_callable(
        inst: typing.Callable,
        use_union: bool,
        state: State) -> typing.Type[typing.Dict[KT, VT]]:
    if 'lambda' in str(inst):
        result = _get_type_lambda(inst, use_union, state)
    else:
        result = typing.Callable
        sig = inspect.signature(inst)
        args = [_map_empty(param.annotation)
                for param in sig.parameters.values()]
        return_type = NoneType
        if sig.return_annotation != Empty:
            return_type = sig.return_annotation
        if args or return_type != NoneType:
            if inspect.iscoroutinefunction(inst):
                return_type = typing.Awaitable[return_type]
            result = typing.Callable[args, return_type]
    return result


def _get_type_lambda(
        inst: typing.Callable,
        use_union: bool,
        state: State) -> typing.Type[typing.Dict[KT, VT]]:
    args = [Unknown for _ in inspect.signature(inst).parameters]
    return_type = Unknown
    return typing.Callable[args, return_type]


def _get_type_dict(inst: typing.Dict[KT, VT],
                   use_union: bool,
                   state: State) -> typing.Type[typing.Dict[KT, VT]]:
    from typish.functions._get_args import get_args

    t_list_k = _get_type_iterable(list(inst.keys()), use_union, state)
    t_list_v = _get_type_iterable(list(inst.values()), use_union, state)
    t_k_tuple = get_args(t_list_k)
    t_v_tuple = get_args(t_list_v)
    return typing.Dict[t_k_tuple[0], t_v_tuple[0]]


def _flatten(l: typing.Iterable[typing.Iterable[typing.Any]]) -> typing.List[typing.Any]:
    result = []
    for x in l:
        result += [*x]
    return result


def _map_empty(annotation: type) -> type:
    result = annotation
    if annotation == Empty:
        result = typing.Any
    return result
