#!/bin/python3

#> Imports
import sys
import types
import argparse
import functools
from importlib import util as iutil
#</Imports

#> Header >/
__all__ = ('eprint',
           'menu_arg',
           'exec_entrypoint')

# IO
eprint = functools.partial(print, file=sys.stderr)

# Argparse
def menu_arg(ap: argparse.ArgumentParser, dest: str, name: str, *aliases: str, **kwargs):
    ap.add_argument(f'--{name}', *aliases, dest=dest, action='store_const', const=name, **kwargs)

# FlexiLynx
runlevels = ('__load__', '__setup__')
def exec_entrypoint(args: argparse.Namespace) -> types.ModuleType | None:
    ep = args.entrypoint or args.root
    if ep.is_dir(): ep /= '__init__.py'
    eprint(f'Bringing FlexiLynx to runlevel {args.runlevel} from {ep}')
    if args.runlevel < 2:
        eprint(f'Warning: runlevel {args.runlevel} will {"probably " if args.runlevel == 1 else ""}not work and is purely allowed for semantics')
    if args.runlevel == -1: return None
    ep = iutil.spec_from_file_location('<FlexiLynx entrypoint>', ep,
                                       submodule_search_locations=(ep.parent,)).loader.load_module()
    for r in range(0, args.runlevel):
        eprint(f'Calling: <entrypoint>.{runlevels[r]}()')
        getattr(ep, runlevels[r])()
    return ep
