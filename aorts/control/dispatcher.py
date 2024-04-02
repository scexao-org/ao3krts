'''
A simple ad-hoc server class

Multiple objects can be registered, and the dispatching is performed based on the first argument.

Each object is expected to implement the protocol, and use its tcp_dispatch function,
possibly to dispatch the command to a given function call
'''
from __future__ import annotations

import typing as typ

import threading

import logging

logg = logging.getLogger(__name__)

from swmain.network.tcpserver import InvokableObjectForServer


def locking_func_decorator(func):

    def lock_wrapped_func(self: DocoptDispatchingObject, *args, **kwargs):
        if self.SERVER_LOCK is not None:
            with self.SERVER_LOCK:
                return func(self, *args, **kwargs)
        else:
            return func(self, *args, **kwargs)

    return lock_wrapped_func


class DocoptDispatchingObject(InvokableObjectForServer):
    # From superclass
    # NAME: str
    # DESCR: str
    # SERVER_LOCK: threading.Lock | None = None

    # Docstring that can be use to ensure command validity before function dispatch
    DOCOPTSTR: str
    DOCOPTCASTER: dict[str, type]

    # Mapper to dispatch function calls based on the command
    TCP_CALLS: dict[str, typ.Callable]

    def __init__(self, common_lock: threading.Lock | None = None) -> None:
        self.SERVER_LOCK = common_lock
        self.TCP_CALLS = {'test': self.sample_locked_func}

    def function_dispatch(self, cmd: str) -> str:
        '''
            This is a stub for reference, where a
            given implementing class could use
            1 - docopt for argument checking
            2 - the inner TCP_CALLS dictionary for inner dispatching
        '''
        import docopt
        try:
            argdict = docopt.docopt(self.DOCOPTSTR, cmd)
            print(argdict)
            for arg in argdict:
                if arg in self.DOCOPTCASTER and argdict[arg] is not None:
                    try:
                        argdict[arg] = self.DOCOPTCASTER[arg](argdict[arg])
                    except ValueError as err:  # Can't cast:
                        return str(err) + self.DOCOPTSTR
        except docopt.DocoptExit:
            return self.DOCOPTSTR

        cmd_head, *_ = cmd.split(None, 1)

        return self.TCP_CALLS[cmd_head.lower()](**argdict)

    @classmethod
    def main(cls):
        '''
        This turns this class into a shell-invokable.
        On the conditions that it is bound to an entrypoint in pyproject.toml
        '''
        import sys
        instance = cls()
        print(' '.join(sys.argv[1:]))
        return instance.function_dispatch(' '.join(sys.argv[1:]))

    def set_lock_obj(self, lock: threading.Lock) -> None:
        self.SERVER_LOCK = lock

    @locking_func_decorator
    def sample_locked_func(self) -> str:
        import time
        time.sleep(1.0)
        return "OK."
