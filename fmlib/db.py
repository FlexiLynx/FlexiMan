#!/bin/python3

#> Imports
import click
import types
import atexit
import typing
import hashlib
import threading
import contextlib
from pathlib import Path

from . import FLBinder, FLType
#</Imports

#> Header >/
__all__ = ('Controller', 'State')

class State(typing.NamedTuple):
    '''
        A result of a database read, or a state to write to a database
        `expl` are explicitly installed packages, `deps` are dependencies
        Note that setting `chksum` to `NotImplemented` is only allowed when
            calculating the checksum
    '''
    mtime: int

    expl: frozenset[str]
    deps: frozenset[str]

    chksum: bytes | typing.Literal[NotImplemented]

    @FLBinder._fl_bindablem
    def mkchksum(self, fl: FLType) -> bytes:
        return hashlib.new(fl.core.util.hashtools.ALGORITHM_DEFAULT_LOW,
                           fl.core.util.pack.pack(self._replace(chksum=NotImplemented))).digest()

@FLBinder._fl_bindable
class Controller(contextlib.AbstractContextManager):
    '''Acts as an interface to a database file, handling locking and returning of states'''
    __slots__ = ('bound', 'path',
                 'rlock', 'flock',
                 '_dbfp', '_packer', '_db_state_noexist')

    PACKAGE_DB_FILENAME = 'packages_db.pakd'
    PACKAGE_DB_LOCKNAME = f'{PACKAGE_DB_FILENAME}.lock'

    def __init__(self, fl: FLType, path: Path):
        self.bound = fl
        self.path = path
        self.rlock = threading.RLock()
        self.flock = self.bound.core.util.parallel.FLock(path/self.PACKAGE_DB_LOCKNAME, self.rlock)
        self._dbfp = self.path / self.PACKAGE_DB_FILENAME
        self._packer = self.bound.core.util.pack.Packer(reduce_namedtuple=self.bound.core.util.pack.ReduceNamedtuple.AS_DICT)
        self._db_state_noexist = State(mtime=0, expl=frozenset(), deps=frozenset(), chksum=NotImplemented)
        self._db_state_noexist = self._db_state_noexist._replace(chksum=self._db_state_noexist.mkchksum(self.bound))

    def __enter__(self):
        self.flock.acquire()
    def __exit__(self, exc_type: type[Exception] | None, exc_value: typing.Any, traceback: types.TracebackType | None):
        self.flock.release()

    def read(self, *, allow_unlocked_read: bool = False, allow_nonexist_read: bool = True) -> State:
        '''
            Reads a `State` from the database
            If `allow_unlocked_read` is false, and the file-lock (`.flock`, `packages_db.pakd.lock`) is not obtained,
                then a `RuntimeError` is raised
                Note that the normal lock (`.rlock`) is still obtained for reading,
                    which in turn blocks the file-lock; even if `allow_unlocked_read` is true
            If `allow_nonexist_read` is false, and the database file (`packages_db.pakd`) doesn't exist,
                a `FileNotFoundError` is raised; otherwise, an empty `State` is returned with an `mtime` of `-1`
        '''
        with self.rlock:
            if not (allow_unlocked_read or self.flock.held):
                raise RuntimeError('Refusing to read from the database without holding the file-lock when allow_unlocked_read is false')
            if not self._dbfp.exists():
                if allow_nonexist_read: return self._db_state_noexist
                raise FileNotFoundError('Refusing to read from the database when it doesn\'t exist and allow_nonexist_read is false')
            return State(**self._packer.unpack(self._dbfp.read_bytes())[0])
    def write(self, s: State):
        '''
            Writes a `State` to the database, automatically calculating its checksum in the process
            Raises `RuntimeError` if the file-lock (`.flock`, `packages_db.pakd.lock`) is not obtained
        '''
        with self.rlock:
            if not self.flock.held:
                raise RuntimeError('Refusing to write a state to the database without holding the file-lock')
            self._dbfp.write_bytes(self._packer.pack(s._replace(chksum=s.mkchksum(self.bound))))
