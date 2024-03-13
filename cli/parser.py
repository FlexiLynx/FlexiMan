#!/bin/python3

#> Imports
import click
import typing
from enum import IntEnum

from . import operations
#</Imports

#> Header >/
__all__ = ('ExitCode', 'split_operation')

ExitCode = IntEnum('ExitCode', {'SUCCESS': 0,
                                'GENERIC': 1,
                                'IMPROPER_USAGE': 2})

def split_operation(args: typing.Sequence[str]) -> tuple[operations.Operation | ExitCode, typing.Sequence[str] | None]:
    if not (args and args[0].startswith('-') and (len(args[0]) > 1)): # catches: ``, `-`
        click.echo('Error: missing operation', err=True)
        return (ExitCode.IMPROPER_USAGE, None)
    arg,*args = args
    if len(arg) > 2: # catches: `-Xx`, `--x`
        if arg[1] == '-': # catches: `--x`
            if (op := operations.op_from_long(arg[2:])) is not None: return (op, args)
            click.echo(f'Error: unknown long-form operation {arg[2:]!r}', err=True)
            return (ExitCode.IMPROPER_USAGE, None)
        args.insert(0, f'-{arg[2:]}') # remove `x` from `-Xx` and add it to remaining args as `-x`
    # catches: `-X`
    if (op := operations.op_from_short(arg[1])) is not None: return (op, args)
    click.echo(f'Error: unknown short-form operation {arg[1]!r}')
    return (ExitCode.IMPROPER_USAGE, None)
