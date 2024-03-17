#!/bin/python3

#> Imports
import sys
import json
import typing
import argparse
import traceback
import contextlib
from pathlib import Path

from .. import common
from ..parser import ExitCode

from .. import _eprint
#</Imports

#> Header >/
__all__ = ('cli', 'parser')

parser = argparse.ArgumentParser(prog=f'{sys.argv[0]} -F')
common.root(parser)
load_db = common.database(parser)
exec_ep = common.entrypoint(parser, 2)
menu = parser.add_mutually_exclusive_group(required=True)
parser.add_argument('-p', '--as-path', help='Treat targets as paths to packages, rather than package IDs (note that this will stop the loading of the packages database)')
parser.add_argument('--ignore-missing', help='Ignore missing paths/packages--simply do not output', action='store_true')
parser.add_argument('--ignore-invalid', help='Ignore paths that are not packages')
parser.add_argument('-j', '--json', help='Output in JSON format', action='store_true')
parser.add_argument('targets', nargs='*')

def cli(args: typing.Sequence[str]):
    args = parser.parse_args(args)
    ep,fmlib = exec_ep(args)
    if args.as_path: db = None
    else:
        db = load_db(args, fmlib)
        _eprint('Obtaining database lock...')
    targets = dict.fromkeys(args.targets).keys()
    with contextlib.nullcontext() if args.as_path else db:
        if args.as_path:
            targets = dict(zip(targets, map(Path, targets)))
        if not args.as_path:
            _eprint('Reading database...')
            state = db.read()
            missing = targets - (state.expl | state.deps)
            _eprint('Some packages are not listed in the database:\n{", ".join(missing)}')
            if missing and (not args.ignore_missing):
                _eprint('Error: some packages were not listed in the database (pass --ignore-missing to ignore)')
                return ExitCode.GENERIC
            targets = {t: fmlib.packages.id_to_name(t) for t in targets}
        exists = ep.FlexiLynx.core.util.maptools.filter_keys(Path.exists, targets)
        if missing := (targets.keys() - exists.keys()):
            _eprint(f'Missing {len(missing)} director(y/ies):')
            if args.as_path:
                for k in missing: _eprint(targets[k])
            else:
                for k in missing: _eprint(f'{k}: {targets[k]}')
            if not args.ignore_missing:
                _eprint('Error: some targets\' directories are missing (pass --ignore-missing to ignore)')
                return ExitCode.GENERIC
        packages = {}
        for id,path in exists.items():
            try:
                packages[id] = ep.FlexiLynx.core.frameworks.blueprint.Package(path)
            except Exception as e:
                _eprint(f'Invalid package {path if args.as_path else f"{id} ({path})"}:')
                _eprint((''.join(traceback.format_exc_only(e))).strip())
                if args.ignore_invalid: continue
                _eprint('Error: at least one package was invalid (pass --ignore-invalid to ignore)')
                return ExitCode.GENERIC
        _eprint(f'Dispatching to action_{args.action}()')
        return globals()[f'action_{args.action}'](args, packages, fmlib, ep.FlexiLynx, db)
