#!/bin/python3

#> Imports
import typing
import argparse
from pathlib import Path

from .. import common
#</Imports

#> Header >/
__all__ = ('cli', 'parser')

parser = argparse.ArgumentParser()
common.root(parser)
common.database(parser)

def cli(args: typing.Sequence[str]):
    print(parser.parse_args(args))
