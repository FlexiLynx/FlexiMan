#!/bin/python3

#> Imports
import typing
from dataclasses import dataclass, field

from .ops import database
from .ops import files
#</Imports

#> Header >/
_operations = ('SYNC', 'REMOVE', 'DATABASE', 'FILES', 'DEPTEST', 'HELP')
__all__ = ('operations', 'op_from_short', 'op_from_long') + _operations

# Base class
@dataclass(slots=True)
class Operation:
    name: str
    short: str | None = field(default=None, kw_only=True)
    argstr: str | None
    desc: str
    cli: typing.Callable[[typing.Sequence[str]], None]

    def __post_init__(self):
        self.name = self.name.upper()
        if self.short is None: self.short = self.name[0].upper()

# Instances
SYNC = Operation('sync', '!WIP:argstr!', '!WIP:desc!', NotImplemented)
REMOVE = Operation('remove', '!WIP:argstr!', '!WIP:desc!', NotImplemented)
DATABASE = Operation('database', '!WIP:argstr!', '!WIP:desc!', database.cli)
FILES = Operation('files', '!WIP:argstr!', '!WIP:desc!', files.cli)
DEPTEST = Operation('deptest', '!WIP:argstr!', '!WIP:desc!', NotImplemented, short='T')
HELP = Operation('help', None, 'Basic information/usage', NotImplemented, short='h')

operations = {opn: globals()[opn] for opn in _operations}

# Functions
_shortdict = {op.short: op for op in operations.values()}
def op_from_short(s: str) -> Operation | None:
    return _shortdict.get(s, None)
_longdict = {op.name.lower(): op for op in operations.values()}
def op_from_long(l: str) -> Operation | None:
    return _longdict.get(l, None)
