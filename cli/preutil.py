#!/bin/python3

#> Imports
import sys
import argparse
import functools
#</Imports

#> Header >/
__all__ = ('eprint',
           'menu_arg')

# IO
eprint = functools.partial(print, file=sys.stderr)

# Argparse
def menu_arg(ap: argparse.ArgumentParser, dest: str, name: str, *aliases: str, **kwargs):
    ap.add_argument(f'--{name}', *aliases, dest=dest, action='store_const', const=name, **kwargs)
