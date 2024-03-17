#!/bin/python3

#> Imports
import sys
import typing
import argparse
import importlib

from cli import parsers
#</Imports

#> Header
#</Header

#> Main >/
def main(args: typing.Sequence[str]):
    # preprocess args in case of short operation
    args = parsers.fix_short_operation(args)
    # execute initial preparser
    pre,args = parsers.pre_parser.parse_known_args(args)
    # dispatch the operation
    ## fetch its module
    op = importlib.import_module(f'cli.operations.{pre.op}')
    ## create and fill its parser
    parser = argparse.ArgumentParser(f'{sys.argv[0]} -{parser.operations[args.op]}/--{args.op}')
    op.fill(parser)
    ## dispatch to its parser
    args = parser.parse_args(args)
    ## dispatch to its main
    try: op.main(parser)
    except parsers.ExitCode as e: sys.exit(e.code)

if __name__ == '__main__': main(sys.argv[1:])
