#!/bin/python3

#> Imports
import typing
import argparse
from pathlib import Path
#</Imports

#> Header >/
__all__ = ('basecli', 'common', 'database')

def root(ap: argparse.ArgumentParser):
    ap.add_argument('-r', '--root', type=Path, help='Set an alternative FlexiLynx root location', metavar='PATH', default=Path('.'))
def database(ap: argparse.ArgumentParser):
    ap.add_argument('-b', '--dbpath', type=Path, help='Set an alternative database directory', metavar='PATH', default=None)
