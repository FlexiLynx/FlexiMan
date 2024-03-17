#!/bin/python3

#> Imports
import types
import typing
import argparse
from pathlib import Path

from . import parsers
from . import preutil

import FlexiLynx
#</Imports

#> Header >/
__all__ = ('fmlib',
           'handle_database')

from fmlib import total_autobind as fmlib

# Argparse
def handle_database(ap: argparse.ArgumentParser, ensure_exists: bool = True) -> typing.Callable[[argparse.Namespace], fmlib.db.Controller]:
    # add arguments
    ap.add_argument('-b', '--dbpath', type=Path, help='Set an alternative database directory', metavar='PATH', default=None)
    # create and return handler
    def database_handler(args: argparse.Namespace) -> fmlib.db.Controller:
        dbpath = args.root if args.dbpath is None else args.dbpath
        if dbpath.is_file():
            preutil.eprint(f'Error: -b/--dbpath must be a directory, not a file')
            raise parsers.DoExit(parsers.ExitCode.USAGE | parsers.ErrorLocation.DATABASE)
        if not (dbpath/fmlib.db.Controller.PACKAGE_DB_FILENAME).exists():
            preutil.eprint(f'Database file does not exist: {dbpath/fmlib.db.Controller.PACKAGE_DB_FILENAME}')
            if ensure_exists:
                preutil.eprint('Error: an existing database file is required')
                raise parsers.DoExit(parsers.ExitCode.MISSING | parsers.ErrorLocation.DATABASE)
            preutil.eprint('It will be created if modifications are made')
        return fmlib.db.Controller(dbpath)
    return database_handler
