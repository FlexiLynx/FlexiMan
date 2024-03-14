#!/bin/python3

#> Imports
import sys
import typing
import argparse

from cli import parser
from cli import operations
#</Imports

#> Header
#</Header

#> Main >/
def main(args: typing.Sequence[str]):
    # preprocess operation
    op,args = parser.split_operation(args)
    # handle errors
    if isinstance(op, parser.ExitCode):
        if op is parser.ExitCode.IMPROPER_USAGE:
            operations.HELP.cli(())
        sys.exit(op)
    # dispatch to operator cli
    op.cli(args)
if __name__ == '__main__': main(sys.argv[1:])
