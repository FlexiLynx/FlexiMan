#!/bin/python3

#> Imports
import sys
import typing
import argparse
import importlib

from cli import parsers
from cli import preutil
#</Imports

#> Header
#</Header

#> Main >/
def main(args: typing.Sequence[str]):
    # preprocess args in case of short operation
    args = parsers.fix_short_operation(args)
    # execute initial preparser
    pre,args = parsers.pre_parser.parse_known_args(args)
    # dispatch main help if needed
    if pre.help:
        if pre.op is None:
            parsers.pre_parser.print_help()
            return
    # bring FlexiLynx to the desired runlevel
    else: ep = preutil.exec_entrypoint(pre)
    # dispatch the operation
    ## fetch its module
    op = importlib.import_module(f'cli.operations.{pre.op}')
    ## create and fill its parser
    parser = argparse.ArgumentParser(f'{sys.argv[0]} -{parsers.operations[pre.op]}/--{pre.op}')
    op.fill(parser, pre.help)
    ## dispatch operator's help if needed
    if pre.help:
        parser.print_help()
        return
    ## dispatch to its parser
    args = parser.parse_args(args)
    args.__dict__.update(pre.__dict__)
    ## dispatch to its main
    try: op.main(ep, args)
    except parsers.DoExit as e: sys.exit(e.code)

if __name__ == '__main__': main(sys.argv[1:])
