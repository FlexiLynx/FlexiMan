#!/bin/python3

#> Imports
import sys
import click
import typing

from cli import parser
from cli import operations
#</Imports

#> Header
#</Header

#> Main >/
def main(args: typing.Sequence[str]):
    # preprocess operation
    op,args = parser.split_operation(args)
    click.echo(repr(op), file=sys.stderr)
    # handle errors
    if isinstance(op, parser.ExitCode):
        if op is parser.ExitCode.IMPROPER_USAGE:
            operations.HELP.cli()
        sys.exit(op)
    # dispatch to operator cli
    op.cli()
if __name__ == '__main__': main(sys.argv[1:])
