#!/bin/python3

'''Utilities for manipulating FlexiLynx/blueprint packages'''

#> Imports
import typing
from pathlib import Path

from . import FLType
from . import _total_autobind_store
#</Imports

#> Header >/
__all__ = ('PackageType',
           'setup_from_url', 'setup_from_bytes', 'setup_from_dict', 'setup_from_blueprint',
           'id_to_name',
           'package_from_dir')

# Package typehint
type PackageType = object

# Setup functions
@_total_autobind_store.bindable_func('packages')
def setup_from_url(fl: FLType, url: str, to: Path, *, fetchfn: typing.Callable[[str], bytes] | None = None) -> PackageType:
    '''
        Sets up and returns the package with a blueprint from `url` to the path `to`
        See `help(setup_from_blueprint)` for more information
    '''
    return setup_from_bytes(fl, (fl.core.util.net.fetch1 if fetchfn is None else fetchfn)(url), to)
@_total_autobind_store.bindable_func('packages')
def setup_from_bytes(fl: FLType, data: bytes, to: Path) -> PackageType:
    '''
        Sets up and returns the package with a blueprint from `data` to the path `to`
        See `help(setup_from_blueprint)` for more information
    '''
    return setup_from_blueprint(fl, fl.core.frameworks.blueprint.Blueprint.deserialize(data.decode()), to)
@_total_autobind_store.bindable_func('packages')
def setup_from_dict(fl: FLType, d: dict, to: Path) -> PackageType:
    '''
        Sets up and returns the package with a blueprint from `d` to the path `to`
        See `help(setup_from_blueprint)` for more information
    '''
    return setup_from_blueprint(fl, fl.core.frameworks.blueprint.Blueprint.deserialize_from_dict(d), to)
@_total_autobind_store.bindable_func('packages')
def setup_from_blueprint(fl: FLType, bp: 'Blueprint', to: Path) -> PackageType:
    '''
        Sets up and returns the package with blueprint `bp` to the path `to`
        Note that this only `.install()`s the `blueprint.json` and `package_db.pakd`,
            executing `.sync()` on the package may be necessary
        If the directory `to` doesn't exist, it is created
    '''
    to.mkdir(exist_ok=True, parents=True)
    pkg = fl.core.frameworks.blueprint.Package(bp)
    pkg.install(to)
    pkg.save()
    return pkg

# String functions
def id_to_name(id: str) -> str:
    '''Converts an ID to its corresponding standard folder name'''
    return id.replace(':', '-').replace('/', '_')

# Directory functions
@_total_autobind_store.bindable_func('packages')
def package_from_dir(fl: FLType, d: Path) -> PackageType | None:
    '''
        Gets a package from a directory
        Returns `None` if the directory doesn't exist or is not a package
    '''
    if not d.exists(): return None
    try:
        return fl.core.frameworks.blueprint.Package(d)
    except Exception: return None
