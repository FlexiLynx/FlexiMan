#!/bin/python3

#> Imports
import types
import typing
import argparse
from pathlib import Path
from importlib import util as iutil

from . import _eprint

try: import fmlib
except ModuleNotFoundError as mnfe:
    try: from .. import fmlib
    except ImportError as ie:
        raise ExceptionGroup('Could neither import fmlib from path, nor could it be imported relatively', mnfe, ie)
#</Imports

#> Header >/
__all__ = ('fmlib',
           'UsageError',
           'common', 'database', 'entrypoint',
           'menu_arg')

class UsageError(Exception): pass

# Argument adders
def root(ap: argparse.ArgumentParser):
    ap.add_argument('-r', '--root', type=Path, help='Set an alternative FlexiLynx root location', metavar='PATH', default=Path('.'))
def database(ap: argparse.ArgumentParser):
    ap.add_argument('-b', '--dbpath', type=Path, help='Set an alternative database directory', metavar='PATH', default=None)
    def load_database(args: argparse.Namespace, fmlib: fmlib.FLBinder) -> fmlib.db.Controller:
        if args.dbpath is None: args.dbpath = args.root
        elif not args.dbpath.is_dir():
            raise TypeError('-b/--dbpath should be a directory, not a file')
        if not (args.dbpath/fmlib.db.Controller.PACKAGE_DB_FILENAME).exists():
            _eprint(f'Warning: database does not exist, it may be created')
        _eprint(f'Database: {args.dbpath/fmlib.db.Controller.PACKAGE_DB_FILENAME}')
        return fmlib.db.Controller(args.dbpath)
    return load_database

def entrypoint(ap: argparse.ArgumentParser, runlevel: typing.Literal[0, 1, 2]) -> typing.Callable[[typing.Sequence[str]], None]:
    ap.add_argument('-e', '--entrypoint', type=Path, help='Set an alternative FlexiLynx entrypoint (either the path containing `__entrypoint__.py` and `__init__.py`, or the file to use instead), defaults to `--root`', metavar='PATH', default=None)
    def run_entrypoint(args: argparse.Namespace) -> tuple[types.ModuleType, fmlib.FLBinder | None]:
        if args.entrypoint is None: args.entrypoint = args.root/'__init__.py'
        elif args.entrypoint.is_dir(): args.entrypoint /= '__init__.py'
        _eprint(f'Attempting to fetch entrypoint: {args.entrypoint} | runlevel: {runlevel}')
        global ep
        ep = iutil.spec_from_file_location('<FlexiLynx entrypoint>', args.entrypoint, submodule_search_locations=(args.entrypoint.parent,)).loader.load_module()
        if runlevel < 1: return (ep, None)
        _eprint('__load__()')
        ep.__load__()
        _eprint('Binding FMLib')
        fmlbound = fmlib.FLBinder(ep.FlexiLynx)
        _eprint(repr(fmlbound))
        if runlevel < 2: return (ep, fmlbound)
        _eprint('__setup__()')
        ep.__setup__()
        return (ep, fmlbound)
    return run_entrypoint

# Argument helpers
def menu_arg(ap: argparse.ArgumentParser, dest: str, short: str | None, long: str, *args, **kwargs):
    params = (f'--{long}',) if short is None else (f'-{short}', f'--{long}')
    ap.add_argument(*params, *args, dest=dest, action='store_const', const=long, **kwargs)
