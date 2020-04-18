import inspect
import re
from functools import wraps
from typing import Dict, Optional, Callable

_DEFAULT_PARAM_NAME = 'hint'


class _Hintable:
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
        code_context = previous_frame.code_context[0].strip()
        hint_str = self._extract_hint(code_context)

        hint = None
        if hint_str is not None:
            hint = self._to_cls(hint_str, previous_frame.frame.f_globals)

        kwargs_ = {**kwargs, self._param: kwargs.get(self._param, hint or hint_str)}
        return self._decorated(*args, **kwargs_)

    def _extract_hint(self, code_context: str) -> Optional[str]:
        result = None
        regex = (
            r'.+?(:(.+?))?=\s*'  # e.g. 'x: int = ', $2 holds hint
            r'.*?{}\s*\(.*?\)\s*'  # e.g. 'func(...) '
            r'(#\s*type\s*:\s*(\w+))?\s*'  # e.g. '# type: int ', $4 holds hint
        ).format(self._decorated.__name__)
        match = re.search(regex, code_context)

        if match:
            # Type hints take precedence over MyPy style hints.
            result = match.group(2) or match.group(4)

        if result is not None:
            result = result.strip()
            if self._is_between(result, '\'') or self._is_between(result, '"'):
                # Remove any quotes that surround the hint.
                result = result[1:-1].strip()

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
    :param decorated: a function or method.
    :param param: the name of the parameter that receives the type hint.
    :return: the decorated function/method wrapped into a new function.
    """
    if decorated is not None:
        wrapper = _get_wrapper(decorated, param, 2)
    else:
        wrapper = lambda decorated_: _get_wrapper(decorated_, param, 2)

    return wrapper
