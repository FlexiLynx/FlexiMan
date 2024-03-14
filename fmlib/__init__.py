#!/bin/python3

'''FlexiMan library'''

#> Imports
import sys
import typing
import functools
from types import ModuleType
#</Imports

#> Package >/
__all__ = ('FLType', 'FLBinder', 'db', 'packages')

# Objects
FLType = typing.Annotated[ModuleType, 'FlexiLynx']

class FLBinder:
    '''
        Wraps this library to automatically call functions with a module
        When first constructed, all attributes are obtained from the root library
        Functions wrapped with `@FLBinder._fl_bindable[m]`
    '''
    __slots__ = ('_bound', '_current', '__wrapped__')

    _UNBOUND_CURRENT = object()

    def __new__(cls, fl: FLType, *, _current: typing.Any = _UNBOUND_CURRENT) -> typing.Self | typing.Callable:
        if getattr(_current, '_fl_bindable', False):
            return functools.partial(_current, fl)
        if getattr(_current, '_fl_bindablem', False):
            return functools.partialmethod(_current, fl)
        return super().__new__(cls)
    def __init__(self, fl: FLType, *, _current: typing.Any = _UNBOUND_CURRENT):
        self._bound = fl
        self._current = sys.modules[__name__] if _current is FLBinder._UNBOUND_CURRENT else _current
    def __getattr__(self, attr: str) -> typing.Self:
        return type(self)(self._bound, _current=getattr(self._current, attr))
    def __setattr__(self, attr: str, val: typing.Any):
        if attr in self.__slots__:
            return super().__setattr__(attr, val)
        setattr(self._current, attr, val)
    def __delattr__(self, attr: str):
        delattr(self._current, attr)
    def __dir__(self) -> typing.Sequence[str]:
        return dir(self._current)
    def __repr__(self) -> str:
        return f'<FLBinder bound={self._bound!r} current={self._current!r}>'

    @staticmethod
    def _fl_bindable(f: typing.Callable) -> typing.Callable:
        '''Marks a function as being bindable via `FLBinder`'''
        f._fl_bindable = True
        return f
    @staticmethod
    def _fl_bindablem(f: typing.Callable) -> typing.Callable:
        '''Marks a method as being bindable via `FLBinder`'''
        f._fl_bindablem = True
        return f

# Submodules
from . import db
from . import packages
