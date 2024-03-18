#!/bin/python3

'''FlexiMan library'''

VERSION = '1.0.0'

#> Imports
import sys
import typing
import inspect
import functools
from types import ModuleType
#</Imports

#> Package >/
__all__ = ('VERSION', 'FLType', 'db', 'packages')

# Objects
type FLType = typing.Annotated[ModuleType, 'FlexiLynx']

class _TotalAutobindStore:
    __slots__ = ('marked_f', 'marked_c')
    def __init__(self):
        self.marked_f = {}
        self.marked_c = {}
    @functools.cache
    def bindable_func(self, where: str) -> typing.Callable:
        def binder(f: typing.Callable) -> typing.Callable:
            self.marked_f.setdefault(where, []).append(f)
            return f
        return binder
    @functools.cache
    def bindable_cls(self, where: str) -> type:
        def binder(c: type) -> type:
            self.marked_c.setdefault(where, []).append(c)
            return c
        return binder
    def bindable_meth(self, m: typing.Callable) -> typing.Callable:
        m._totalautobindable = True
        return m
_total_autobind_store = _TotalAutobindStore()

# Submodules
from . import db
from . import packages
