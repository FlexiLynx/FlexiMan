#!/bin/python3

#> Imports
import sys
import types
import argparse
from functools import partial

from .. import preutil
from .. import parsers
from .. import postutil

import FlexiLynx
#</Imports

#> Header >/
__all__ = ('fill', 'main', 'actions')

def fill(ap: argparse.ArgumentParser):
    menu = ap.add_mutually_exclusive_group(required=True)
    menu = partial(preutil.menu_arg, menu, 'action')
    menu('check', '-k', help='Test database checksum')
    menu('asdeps', help='Mark packages as non-explicitly installed')
    menu('asexplicit', help='Mark packages as explicitly installed')
    ap.add_argument('--ignore-missing', help='Don\'t fail if any target packages are missing from the database', action='store_true')
    ap.add_argument('targets', nargs='*', help='Package IDs to target')
    # LGTM way to transfer the returned function from `postutil.handle_database()` to `main()`
    ap.add_argument('--%dbgetter%', help=argparse.SUPPRESS, default=postutil.handle_database(ap, False),
                    action=preutil.RaiseAction, const=TypeError(f'Why would you do this{"‽" if sys.getdefaultencoding == "utf-8" else "?!"}'))
def main(ep: types.ModuleType, args: argparse.Namespace):
    db = getattr(args, '%dbgetter%')(args)
    print(1)
    preutil.eprint('Obtaining database lock...')
    try:
        with db: actions[args.action](args, db)
    finally:
        preutil.eprint('Database lock successfully released')

def _action_check(args: argparse.Namespace, db: postutil.fmlib.db.Controller):
    if args.targets:
        preutil.eprint('Error: extraneous arguments ("targets" should not be supplied with -k/--check)')
        raise parsers.DoExit(parsers.ExitCode.USAGE | parsers.ErrorLocation.DATABASE)
    preutil.eprint('Reading database')
    state = db.read()
    preutil.eprint('Generating checksum')
    chksum = state.mkchksum()
    print(f'Reported:   {FlexiLynx.core.util.base85.encode(state.chksum)}')
    print(f'Calculated: {FlexiLynx.core.util.base85.encode(chksum)}')
    if state.chksum == chksum:
        print('Checksums match')
        return
    print('Checksums do not match')
    raise parsers.DoExit(parsers.ExitCode.GENERIC | prasers.ErrorLocation.DATABASE)

def _action_as_(expl: bool, args: argparse.Namespace, db: postutil.fmlib.db.Controller):
    if not args.targets:
        preutil.eprint('Nothing to do')
        return
    targets = set(args.targets)
    preutil.eprint('Reading database')
    state = db.read()
    missing = targets - (state.expl.keys() | state.deps.keys())
    if missing:
        preutil.eprint(f'Some targets are not installed:\n{", ".join(missing)}')
        if not args.ignore_missing:
            preutil.eprint('Error: some targets are not installed (pass --ignore-missing to ignore)')
            raise parsers.DoExit(parsers.ExitCode.MISSING | parsers.ErrorLocation.DATABASE)
        targets -= missing
    targets -= (state.expl.keys() if expl else state.deps.keys())
    if not targets:
        preutil.eprint('Nothing to do')
        return
    pop = (state.deps if expl else state.expl).pop
    (state.expl if expl else state.deps).update(zip(targets, map(pop, targets)))
    preutil.eprint('Writing database')
    db.write(state)

actions = {'check': _action_check,
           'asdeps': partial(_action_as_, False),
           'asexplicit': partial(_action_as_, True)}
