[![image](https://img.shields.io/pypi/pyversions/typish.svg)](https://pypi.org/project/typish/)
[![Downloads](https://pepy.tech/badge/typish)](https://pepy.tech/project/typish)
[![Pypi version](https://badge.fury.io/py/typish.svg)](https://badge.fury.io/py/typish)
[![codecov](https://codecov.io/gh/ramonhagenaars/typish/branch/master/graph/badge.svg)](https://codecov.io/gh/ramonhagenaars/typish)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/ramonhagenaars/typish/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/ramonhagenaars/typish/?branch=master)

# Typish

* Functions for thorough checks on types
* Instance checks considering generics
* Typesafe Duck-typing

## Example

```python
>>> from typing import Iterable
>>> from typish import instance_of
>>> instance_of([1, 2, 3], Iterable[int])
True
```

## Installation

```
pip install typish
```

## Content

### Functions

| Function | Description
|---|---
| ``subclass_of(cls: type, *args: type) -> bool`` | Returns whether ``cls`` is a sub type of *all* types in ``args``
| ``instance_of(obj: object, *args: type) -> bool`` | Returns whether ``cls`` is an instance of *all* types in ``args``
| ``get_origin(t: type) -> type`` | Return the "origin" of a generic type. E.g. ``get_origin(List[str])`` gives ``list``.
| ``get_args(t: type) -> typing.Tuple[type, ...]`` | Return the arguments of a generic type. E.g. ``get_args(List[str])`` gives ``(str, )``.
| ``get_alias(cls: T) -> typing.Optional[T]`` | Return the ``typing`` alias for a type. E.g ``get_alias(list)`` gives ``List``.
| ``get_type(inst: T, use_union: bool = False) -> typing.Type[T]`` | Return the (generic) type of an instance. E.g. a list of ints will give ``List[int]``.
| ``common_ancestor(*args: object) -> type`` | Return the closest common ancestor of the given instances.
| ``common_ancestor_of_types(*args: type) -> type`` | Return the closest common ancestor of the given classes.
| ``get_args_and_return_type(hint: typing.Type[typing.Callable]) -> typing.Tuple[typing.Optional[typing.Tuple[type]], typing.Optional[type]]`` | Get the argument types and the return type of a callable type hint (e.g. ``Callable[[int], str]``). 
| ``get_type_hints_of_callable(func: typing.Callable) -> typing.Dict[str, type]`` | Return the type hints of the parameters of the given callable.
| ``is_type_annotation(item: typing.Any) -> bool`` | Returns whether ``item`` is a ``type`` or a ``typing`` type.


### Types

| Type | Description
|---|---|
| ``T`` | A generic Type var.
| ``KT`` | A Type var for keys in a dict.
| ``VT`` | A type var for values in a dict.
| ``Empty`` | The type of emptiness (= ``Parameter.empty``).
| ``Unknown`` | The type of something unknown.
| ``Module`` | The type of a module.
| ``NoneType`` | The type of ``None``.
| ``EllipsisType`` | The type of ``...``.

### Decorators

#### hintable
This decorator allows one to capture the type hint of a variable that calls a function. If no hint is provided, `None` 
is passed as a value for `hint`.

```python
@hintable
def cast(arg: Any, hint: Type[T]) -> T:
    return hint(arg)

# The type hint on x is passed to cast:
x: int = cast('42')

# It works with MyPy hints as well:
y = cast('42')  # type: int

# Not something you would normally do, but the type hint takes precedence:
z: int = cast('42')  # type: str
```

### Classes

#### SubscriptableType
This metaclass allows a type to become subscriptable.

*Example:*
```python
class MyClass(metaclass=SubscriptableType):
    ...
```
Now you can do:
```python
MyClass2 = MyClass['some args']
print(MyClass2.__args__)
print(MyClass2.__origin__)
```
Output:
```
some args
<class '__main__.MyClass'>
```

#### Something
Define an interface with ``typish.Something``.

*Example:*
```python
Duck = Something['walk': Callable[[], None], 
                 'quack': Callable[[], None]]
```

Anything that has the attributes defined in ``Something`` with the right type is 
considered an instance of that ``Something`` (classes, objects, even modules...).

The builtin ``isinstance`` is supported as well as ``typish.instance_of``.

#### ClsDict
A dictionary that uses instance checking to determine which value to return.
It only accepts types as keys.

This is particularly useful when a function accepts multiple types for an 
argument and you want to split the implementation into separate functions.

*Example:* 
```python

def _handle_str(item):
    ...
    
def _handle_int(item):
    ...

def func(item):
    # Suppose item can be a string or an int, you can use ClsDict to
    # pick a handler function.
    
    cd = ClsDict({
        str: _handle_str,
        int: _handle_int,
    })
    
    handler = cd[item]  # Pick the right handler.
    handler(item)       # Call that handler.
```

#### ClsFunction
A callable that uses `ClsDict` to call the right function.
Below is the same example as above, but slightly modified in 
that it uses `ClsFunction`.

*Example:*

```python
def _handle_str(item):
    ...


def _handle_int(item):
    ...


def func(item):
    # Suppose item can be a string or an int, you can use ClsFunction to
    # delegate to the right handler function.

    function = ClsFunction({
        str: _handle_str,
        int: _handle_int,
    })

    function(item)

```

#### Literal
A backwards compatible variant of typing.Literal (Python3.8). When importing 
`Literal` from `typish`, you will get the `typing.Literal` if it is available.
