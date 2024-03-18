#!/bin/python3

#> Imports
import types
import typing
import argparse
import traceback
import contextlib

from .. import preutil
from .. import parsers
#</Imports

#> Header >/
__all__ = ('fill', 'main', 'actions')

def fill(ap: argparse.ArgumentParser, for_help: bool):
    menu = ap.add_mutually_exclusive_group(required=True)
    ap.add_argument('-p', '--as-path', help='Treat targets as paths to packages, rather than package IDs (note that this will stop the loading of the packages database)')
    ap.add_argument('--ignore-missing', help='Ignore missing paths/packages--simply do not output', action='store_true')
    ap.add_argument('--ignore-invalid', help='Ignore paths that are not packages')
    ap.add_argument('-j', '--json', help='Output in JSON format', action='store_true')
    ap.add_argument('targets', nargs='*')
    # LGTM way to transfer the returned function from `postutil.handle_database()` to `main()`
    if not for_help:
        from .. import postutil
        ap.add_argument('--%dbgetter%', help=argparse.SUPPRESS, default=postutil.handle_database(ap, False),
                        action=preutil.RaiseAction, const=SyntaxError('Not a chance'))
def main(ep: types.ModuleType, args: argparse.Namespace):
    if args.as_path: db = None
    else:
        db = getattr(args, '%dbgetter%')(args)
        preutil.eprint('Obtaining database lock...')
    try:
        with contextlib.nullcontext() if (db is None) else db: main2(args, db)
    finally:
        if db is not None: preutil.eprint('Database lock (should have) successfully released')
def main2(args: argparse.Namespace, db: typing.ForwardRef('postutil.fmlib.db.Controller') | None):
    import FlexiLynx
    from .. import postutil
    targets = FlexiLynx.core.util.frozenorderedset(args.targets)
    if not targets:
        preutil.eprint('Nothing to do')
        return
    if args.as_path: targets = dict(zip(targets, map(Path, targets)))
    else:
        preutil.eprint('Reading database...')
        state = db.read()
        missing = targets - (state.expl | state.deps)
        if missing:
            preutil.eprint(f'Some targets are missing from the database:\n{", ".join(missing)}')
            if not args.ignore_missing:
                preutil.eprint('Error: cannot continue when targets are missing (pass --ignore-missing to ignore)')
                raise parsers.DoExit(parsers.ExitCode.MISSING | parsers.ErrorLocation.PACKAGE)
        targets = {t: args.root/postutil.fmlib.packages.id_to_name(t) for t in targets}
    exists = {t: p for t,p in targets.items() if p.exists()}
    if missing := (targets.keys() - exists.keys()):
        preutil.eprint('Missing {len(missing)} director(y/ies):')
        preutil.eprint('\n'.join(map(str, map(targets.__getitem__, missing)) if args.as_path
                                 else (f'{t}: {targets[t]}' for t in targets)))
        if not args.ignore_missing:
            preutil.eprint('Error: cannot continue when targeted package directories are missing (pass --ignore-missing to ignore')
            raise parsers.DoExit(parsers.ExitCode.MISSING | parsers.ErrorLocation.PACKAGE)
    packages = {}
    for id,path in exists.items():
        try:
            packages[id] = FlexiLynx.core.frameworks.blueprint.Package(path)
        except FileNotFoundError as fnfe:
            preutil.eprint(f'Could not load package {id} (from {path}), as it does not have a blueprint:')
            preutil.eprint((''.join(traceback.format_exc_only(e))).strip())
            ec = parsers.ExitCode.MISSING | parsers.ErrorLocation.BLUEPRINT
        except Exception as e:
            preutil.eprint(f'Could not load package {id} (from {path}):')
            preutil.eprint((''.join(traceback.format_exc_only(e))).strip())
            ec = parsers.ExitCode.INVALID | parsers.ErrorLocation.PACKAGE
        else: continue
        preutil.eprint('Error: cannot continue after failing to load package (pass --ignore-invalid to ignore)')
        raise parsers.DoExit(ec)
    preutil.eprint(f'Loaded {len(packages)} package(s)')
    actions[arg.action](args, db, packages)

actions = {}
