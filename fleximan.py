#!/bin/python3

#> Imports
import os
import sys
import click
import typing
from pathlib import Path
from enum import IntEnum, StrEnum
from importlib import util as iutil
#</Imports

# Get entrypoint
if ep := os.getenv('FLEXILYNX_ENTRYPOINT', None): p = Path(ep)
elif (p := Path('__entrypoint__.py')).exists(): pass
elif (p := Path('../__entrypoint__.py')).exists(): pass
else:
    raise FileNotFoundError('Could not find __entrypoint__.py or ../__entrypoint__.py, maybe set FLEXILYNX_ENTRYPOINT in env?')
sys.path.append(p.parent.as_posix())
__entrypoint__ = iutil.spec_from_file_location('__entrypoint__', p.as_posix()) \
                     .loader.load_module()

#> Header
context_sett = {'help_option_names': ('--help', '-h'), 'max_content_width': 160}
Operation = StrEnum('Operation', {'SYNC': 'S'})
short_to_op = {op.value: op for op in Operation}
long_to_op = {op.name.lower(): op for op in Operation}
operation_doc = '\n'.join(f'{{-{op.value} --{op.name.lower()}}}: {op.name.capitalize()}(ing) operations' for op in Operation)
ExitCode = IntEnum('ExitCode', {'SUCCESS': 0,
                                'GENERIC': 1,
                                'IMPROPER_USAGE': 2})
#</Header

#> Main >/
# Pre-cli
def precli(args: typing.Sequence[str] | None = None) -> tuple[Operation | ExitCode, typing.Sequence[str] | None]:
    '''A Pacman-inspired "package manager" for FlexiLynx'''
    if args is None: args = sys.argv[1:] # sys.argv as default
    if not (args and args[0].startswith('-') and (len(args[0]) > 1)): # ``, `-`
        # args are empty or args[0] doesn't start with '-' or args[0] is only '-'
        click.echo('Error: missing operation', err=True)
        return (ExitCode.IMPROPER_USAGE, None)
    arg,*args = args
    if arg in {'--help', '-h'}: # `--help`, `-h`
        click.echo(click.wrap_text(precli.__doc__, context_sett['max_content_width']))
        click.echo(precli_help)
        return (ExitCode.SUCCESS, None)
    if len(arg) > 2: # `-Xx`, `--xxxx`
        if arg[1] == '-': # `--xxxx`
            if (op := long_to_op.get(arg[2:], None)) is not None:
                return (op, args)
            click.echo(f'Error: unknown long-form operation {arg[2:]!r}', err=True)
            return (ExitCode.IMPROPER_USAGE, None)
        args.insert(0, f'-{arg[2:]}') # `-Xx` to `-X -x`
    # `-X`
    if (op := short_to_op.get(arg[1], None)) is not None: return (op, args)
    click.echo(f'Error: unknown short-form operation {arg[1]!r}', err=True)
    return (ExitCode.IMPROPER_USAGE, None)
precli_help = f'Usage: {sys.argv[0]} COMMAND [ARGS]...\n\n{operation_doc}\n{{-h --help}}: Help (this list)'

# Sync
@click.command(context_settings=context_sett)
@click.option('-s', help='Search database instead of sync', is_flag=True, default=False)
@click.argument('target', nargs=-1)
def sync(*, s: bool, target: typing.Sequence[str]):
    print(f'sync() {s=!r} {target=!r}')

# Main
if __name__ == '__main__':
    op,args = precli()
    if op in ExitCode:
        if op is ExitCode.IMPROPER_USAGE:
            click.echo(precli_help)
        click.echo(repr(op), file=sys.stderr)
        sys.exit(op)
    click.echo(repr(op), file=sys.stderr)
    match op:
        case op.SYNC: sync(args)
