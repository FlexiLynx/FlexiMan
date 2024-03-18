#!/bin/python3

'''
    FlexiMan library
    Automatically imports and binds to `FlexiLynx`
'''

#> Imports
from operator import attrgetter
from types import ModuleType, SimpleNamespace
from inspect import getmembers, isroutine
from functools import partial, partialmethod

try: import FlexiLynx as _FlexiLynx
except ModuleNotFoundError as e:
    e.add_note('Perhaps you have not executed .__load__() on the entrypoint?')
    raise e
#</Imports

#> Package >/
from . import __all__
__all__ += ('unbound',)

from . import *

# Other objects
type FLType = _FlexiLynx.core.util.FlexiSpace

# Binding
unbound = SimpleNamespace()
## Setup
from . import _total_autobind_store
def _boundmodule(modname: str) -> tuple[ModuleType, ModuleType]:
    if hasattr(unbound, modname):
        unboundmod = getattr(unbound, modname)
        boundmod = globals()[modnname]
    else:
        setattr(unbound, modname, (unboundmod := globals()[modname]))
        boundmod = globals()[modname] = ModuleType(f'TotalBound[M]<{modname}>', unboundmod.__doc__)
        boundmod.__dict__.update({'__doc__': unboundmod.__doc__, '__all__': unboundmod.__all__,
                                  '__module__': __name__,
                                 **{a: getattr(unboundmod, a) for a in unboundmod.__all__}})
    return (boundmod, unboundmod)
def _fbindobject(mod: ModuleType, name: str, unbound: object, bound: object):
    setattr(mod, name, bound)
    setattr(bound, 'unbound', unbound)
## Bind functions
for modname,funcs in _total_autobind_store.marked_f.items():
    boundmod,unboundmod = _boundmodule(modname)
    for f in funcs:
        _fbindobject(boundmod, f.__name__, f, partial(f, _FlexiLynx))

## Bind classes
for modname,clses in _total_autobind_store.marked_c.items():
    boundmod,unboundmod = _boundmodule(modname)
    for c in clses:
        _fbindobject(boundmod, c.__name__, c,
                     type(c.__name__, (c,), {'__slots__': (), '__module__': f'{__name__}.{modname}',
                          **{mn: partialmethod(m, _FlexiLynx)
                             for mn,m in getmembers(c, lambda m: getattr(m, '_totalautobindable', False))}}))

# Manual patches
db.Controller._STATE_OBJECT = db.State
db.Controller._TOTAL_AUTOBOUND = True
db.State._TOTAL_AUTOBOUND = True
