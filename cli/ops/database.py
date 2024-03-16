#!/bin/python3

#> Imports
import sys
import typing
import argparse
from pathlib import Path
from functools import partial

from .. import common
from ..parser import ExitCode

from .. import _eprint
#</Imports

#> Header >/
__all__ = ('cli', 'parser',
           'action_check', 'action_asdeps', 'action_asexplicit')

parser = argparse.ArgumentParser(prog=f'{sys.argv[0]} -D')
common.root(parser)
load_db = common.database(parser)
exec_ep = common.entrypoint(parser, 2)
menu = parser.add_mutually_exclusive_group(required=True)
common.menu_arg(menu, 'action', 'k', 'check', help='Test database checksum')
common.menu_arg(menu, 'action', None, 'asdeps', help='Mark packages as non-explicitly installed')
common.menu_arg(menu, 'action', None, 'asexplicit', help='Mark packages as explicitly installed')
missing = parser.add_mutually_exclusive_group(required=False)
missing.add_argument('--ignore-missing', help='Don\'t fail if any targeted packages are missing', action='store_true')
parser.add_argument('targets', nargs='*')

def cli(args: typing.Sequence[str]) -> ExitCode:
    args = parser.parse_args(args)
    ep,fmlib = exec_ep(args)
    try: db = load_db(args, fmlib)
    except common.UsageError as e:
        _eprint(f'Error: {e.message}')
        return ExitCode.IMPROPER_USAGE
    _eprint('Obtaining database lock...')
    with db:
        _eprint(f'Dispatching to action_{args.action}()')
        return globals()[f'action_{args.action}'](args, fmlib, ep.FlexiLynx, db)

def action_check(args: argparse.Namespace, fmlib: common.fmlib.FLBinder, fl: common.fmlib.FLType, db: common.fmlib.db.Controller) -> ExitCode:
    if args.targets:
        _eprint('Error: extraneous arguments ("targets" should not be supplied with -k/--check)')
        return ExitCode.IMPROPER_USAGE
    _eprint('Reading database')
    state = db.read()
    _eprint('Generating checksum')
    chksum = state.mkchksum(fl)
    print(f'Reported:   {fl.core.util.base85.encode(state.chksum)}')
    print(f'Calculated: {fl.core.util.base85.encode(chksum)}')
    if state.chksum == chksum:
        print('Checksums match')
        return ExitCode.SUCCESS
    print('Checksums do not match')
    return ExitCode.GENERIC

def _action_as_(expl: bool, args: argparse.Namespace, fmlib: common.fmlib.FLBinder, fl: common.fmlib.FLType, db: common.fmlib.db.Controller) -> ExitCode:
    if not args.targets:
        _eprint('Nothing to do')
        return ExitCode.SUCCESS
    targets = set(args.targets)
    _eprint('Reading database')
    state = db.read()
    missing = targets - (state.expl.keys() | state.deps.keys())
    if missing:
        _eprint(f'Some targets are not installed:\n{", ".join(missing)}')
        if not args.ignore_missing:
            _eprint('Error: some targets are not installed (pass --ignore-missing to ignore)')
            return ExitCode.GENERIC
        targets -= missing
    targets -= (state.expl.keys() if expl else state.deps.keys())
    if not targets:
        _eprint('Nothing to do')
        return ExitCode.SUCCESS
    pop = (state.deps if expl else state.expl).pop
    (state.expl if expl else state.deps).update(zip(targets, map(pop, targets)))
    _eprint('Writing database')
    db.write(state)
    return ExitCode.SUCCESS
action_asdeps = partial(_action_as_, False)
action_asexplicit = partial(_action_as_, True)
