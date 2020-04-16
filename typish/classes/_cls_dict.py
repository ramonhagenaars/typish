from collections import OrderedDict
from typing import Optional, Any


class ClsDict(OrderedDict):
    """
    ClsDict is a dict that accepts (only) types as keys and will return its
    values depending on instance checks rather than equality checks.
    """
    def __new__(cls, *args, **kwargs):
        """
        Construct a new instance of ``ClsDict``.
        :param args: a dict.
        :param kwargs: any kwargs that ``dict`` accepts.
        :return: a ``ClsDict``.
        """
        from typish.functions._is_type_annotation import is_type_annotation

        if len(args) > 1:
            raise TypeError('TypeDict accepts only one positional argument, '
                            'which must be a dict.')
        if args and not isinstance(args[0], dict):
            raise TypeError('TypeDict accepts only a dict as positional '
                            'argument.')
        if not all([is_type_annotation(key) for key in args[0]]):
            raise TypeError('The given dict must only hold types as keys.')
        return super().__new__(cls, args[0], **kwargs)

    def __getitem__(self, item: Any) -> Any:
        """
        Return the value of the first encounter of a key for which
        ``is_instance(item, key)`` holds ``True``.
        :param item: any item.
        :return: the value of which the type corresponds with item.
        """
        from typish.functions._get_type import get_type
        from typish.functions._subclass_of import subclass_of

        item_type = get_type(item, use_union=True)
        for key, value in self.items():
            if subclass_of(item_type, key):
                return value
        raise KeyError('No match for {}'.format(item))

    def get(self, item: Any, default: Any = None) -> Optional[Any]:
        try:
            return self.__getitem__(item)
        except KeyError:
            return default
