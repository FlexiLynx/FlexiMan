#!/bin/python3

#> Imports
import sys
import types
import typing
import argparse
import functools
from enum import IntEnum
from pathlib import Path

from . import preutil
#</Imports

#> Header >/
__all__ = ('DoExit', 'EXIT_CODE', 'ExitCode', 'ERROR_LOCATION', 'ErrorLocation',
           'operations', 'pre_parser',
           'fix_short_operation')

# Exit codes
class DoExit(Exception):
    __slots__ = ('code',)
    def __init__(self, code: int):
        self.code = code
EXIT_CODE =       0b00001111
ExitCode = IntEnum('ExitCode', {
    'SUCCESS':    0b00000000, # success
    'GENERIC':    0b00000001, # general error
    'USAGE':      0b00000010, # improper CLI usage
    'MISSING':    0b00000011, # missing file
    'INVALID':    0b00000100, # invalid package, database, or blueprint
})
ERROR_LOCATION =  0b11110000
ErrorLocation = IntEnum('ErrorLocation', {
    'NONE':       0b00000000, # success or usage
    'ENTRYPOINT': 0b00010000, # failed whilst attempting to access entrypoint
    'DATABASE':   0b00100000, # failed whilst attempting to access or use database
    'BLUEPRINT':  0b00110000, # failed whilst attempting to access or use blueprint
    'PACKAGE':    0b01000000, # failed whilst attempting to access or use package
})

# Parser
operations = {'database': 'D'}
pre_parser = argparse.ArgumentParser(add_help=False)
## Options
fl_apgroup = pre_parser.add_argument_group('FlexiLynx', 'Configuration for FlexiLynx and its entrypoint')
fl_apgroup.add_argument('-r', '--root', type=Path, help='Set an alternative FlexiLynx root location', default=Path('.'))
fl_apgroup.add_argument('-e', '--entrypoint', type=Path, help='Set an alternative FlexiLynx entrypoint (the default is inferred from the root)', default=None)
fl_apgroup.add_argument('-l', '--runlevel', choices=range(2), help='The run-level to bring FlexiLynx up to (2 is recommended)', default=2)
## Menu
_menu = pre_parser.add_mutually_exclusive_group(required=False)
_menu = functools.partial(preutil.menu_arg, _menu, 'op')
for long,short in operations.items():
    _menu(long, f'-{short}')
del _menu
## Help
pre_parser.add_argument('-h', '--help', action='store_true')

# Parsing
def fix_short_operation(args: typing.Sequence[str]) -> typing.Sequence[str]:
    for i,a in enumerate(args):
        if (len(a) <= 2) or (a[0] != '-'): continue # too short or does not begin with -
        if a[1] == '-': return args # reached explicit end of argument list
        if a[1].isupper(): break # -Xx...
    else: return args # reached end of argument list
    args.pop(i)
    args.insert(i, a[0:2])
    args.insert(i+1, f'-{a[2:]}')
    return args
