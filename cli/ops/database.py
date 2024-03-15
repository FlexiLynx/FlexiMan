#!/bin/python3

#> Imports
import typing
import argparse
from pathlib import Path

from .. import common
from ..parser import ExitCode

from .. import _eprint
#</Imports

#> Header >/
__all__ = ('cli', 'parser',
           'action_check')

parser = argparse.ArgumentParser()
common.root(parser)
load_db = common.database(parser)
exec_ep = common.entrypoint(parser, 2)
excl = parser.add_mutually_exclusive_group(required=True)
common.menu_arg(excl, 'action', 'k', 'check', help='Test database checksum')
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
