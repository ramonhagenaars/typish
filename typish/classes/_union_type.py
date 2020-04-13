class _UnionType(type):
    def __instancecheck__(self, instance):
        return str(instance).startswith('typing.Union')


class UnionType(type, metaclass=_UnionType):
    ...
