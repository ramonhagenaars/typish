import inspect
import re
from functools import wraps
from typing import Dict, Optional, Callable, List

_DEFAULT_PARAM_NAME = 'hint'


class _Hintable:
    _hints_per_frame = {}

    def __init__(
            self,
            decorated: Callable,
            param: str,
            stack_index: int) -> None:
        self._decorated = decorated
        self._param = param
        self._stack_index = stack_index

    def __call__(self, *args, **kwargs):
        stack = inspect.stack()

        previous_frame = stack[self._stack_index]
        frame_id = id(previous_frame.frame)

        if not self._hints_per_frame.get(frame_id):
            code_context = previous_frame.code_context[0].strip()
            hint_strs = self._extract_hints(code_context)
            globals_ = previous_frame.frame.f_globals
            # Store the type hint if any, otherwise the string, otherwise None.
            hints = [self._to_cls(hint_str, globals_) or hint_str or None
                     for hint_str in hint_strs]
            self._hints_per_frame[frame_id] = hints

        hint = (self._hints_per_frame.get(frame_id) or [None]).pop()

        kwargs_ = {**kwargs, self._param: kwargs.get(self._param, hint)}
        return self._decorated(*args, **kwargs_)

    def _extract_hints(self, code_context: str) -> List[str]:
        result = []
        regex = (
            r'.+?(:(.+?))?=\s*'  # e.g. 'x: int = ', $2 holds hint
            r'.*?{}\s*\(.*?\)\s*'  # e.g. 'func(...) '
            r'(#\s*type\s*:\s*(\w+))?\s*'  # e.g. '# type: int ', $4 holds hint
        ).format(self._decorated.__name__)

        # Find all matches and store them (reversed) in the resulting list.
        for _, group2, _, group4 in re.findall(regex, code_context):
            raw_hint = (group2 or group4).strip()
            if self._is_between(raw_hint, '\'') or self._is_between(raw_hint, '"'):
                # Remove any quotes that surround the hint.
                raw_hint = raw_hint[1:-1].strip()
            result.insert(0, raw_hint)

        return result

    def _is_between(self, subject: str, character: str) -> bool:
        return subject.startswith(character) and subject.endswith(character)

    def _to_cls(self, hint: str, f_globals: Dict[str, type]) -> Optional[type]:
        return __builtins__.get(hint, f_globals.get(hint))


def _get_wrapper(decorated, param: str, stack_index: int):
    @wraps(decorated)
    def _wrapper(*args, **kwargs):
        return _Hintable(decorated, param, stack_index)(*args, **kwargs)

    if isinstance(decorated, type):
        raise TypeError('Only functions and methods should be decorated with '
                        '\'hintable\', not classes.')

    if param not in inspect.signature(decorated).parameters:
        raise TypeError('The decorated \'{}\' must accept a parameter with '
                        'the name \'{}\'.'
                        .format(decorated.__name__, param))

    return _wrapper


def hintable(decorated=None, *, param: str = _DEFAULT_PARAM_NAME) -> Callable:
    """
    Allow a function or method to receive the type hint of a receiving
    variable.

    Example:

    >>> @hintable
    ... def cast(value, hint):
    ...     return hint(value)
    >>> x: int = cast('42')
    42

    Use this decorator wisely. If a variable was hinted with a type (e.g. int
    in the above example), your function should return a value of that type
    (in the above example, that would be an int value).

    :param decorated: a function or method.
    :param param: the name of the parameter that receives the type hint.
    :return: the decorated function/method wrapped into a new function.
    """
    if decorated is not None:
        wrapper = _get_wrapper(decorated, param, 2)
    else:
        wrapper = lambda decorated_: _get_wrapper(decorated_, param, 2)

    return wrapper
