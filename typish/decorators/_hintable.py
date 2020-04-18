import inspect
import re
from functools import wraps
from typing import Dict, Optional


_PARAM_NAME = 'hint'


class _Hintable:
    def __init__(self, decorated):
        self._decorated = decorated

    def __call__(self, *args, **kwargs):
        stack = inspect.stack()

        previous_frame = stack[2]
        code_context = previous_frame.code_context[0].strip()
        hint_str = self._extract_hint(code_context)

        hint = None
        if hint_str is not None:
            hint = self._to_cls(hint_str, previous_frame.frame.f_globals)

        kwargs_ = {**kwargs, _PARAM_NAME: kwargs.get(_PARAM_NAME, hint or hint_str)}
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


def hintable(decorated):

    @wraps(decorated)
    def _wrapper(*args, **kwargs):
        return _Hintable(decorated)(*args, **kwargs)

    if isinstance(decorated, type):
        raise TypeError('Only functions and methods should be decorated with '
                        '\'hintable\', not classes.')

    if _PARAM_NAME not in inspect.signature(decorated).parameters:
        raise TypeError('The decorated \'{}\' must accept a parameter with '
                        'the name \'{}\'.'
                        .format(decorated.__name__, _PARAM_NAME))
    return _wrapper
