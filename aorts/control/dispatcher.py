'''
A simple ad-hoc server class

Multiple objects can be registered, and the dispatching is performed based on the first argument.

Each object is expected to implement the protocol, and use its tcp_dispatch function,
possibly to dispatch the command to a given function call
'''
from __future__ import annotations

import click

import typing as typ

import threading

import logging

logg = logging.getLogger(__name__)

from swmain.network.tcpserver import InvokableObjectForServer
'''
    Messy decorator
    Takes a method definition on class S and return an indentical, locking method
    if the SERVER_LOCK is set.

    Note that I use a reentrant lock so that locked function may chain each other.

'''
S = typ.TypeVar('S', bound=InvokableObjectForServer)
P = typ.ParamSpec('P')
R = typ.TypeVar('R')


def locking_func_decorator(
        func: typ.Callable[typ.Concatenate[S, P], R]
) -> typ.Callable[typ.Concatenate[S, P], R]:

    def lock_wrapped_method(self: S, *args: P.args, **kwargs: P.kwargs) -> R:
        if self.SERVER_LOCK is not None:
            with self.SERVER_LOCK:
                return func(self, *args, **kwargs)
        else:
            return func(self, *args, **kwargs)

    return lock_wrapped_method


@click.group()
def cli():
    pass


@cli.group()
@click.pass_context
def net(ctx):
    ctx.obj = Command()


class Command:

    @net.command('ip')
    @click.pass_obj
    def get_public_ip(self, *args):
        print('Invoking get_public_ip')


def main() -> None:
    cli()


if __name__ == "__main__":

    c = Command()
    c.get_public_ip()
    main()


class ClickInvokableObjectForServer(InvokableObjectForServer):

    def invoke_call(self, argstring: str) -> typ.Any:
        self.click_invokator(['click_invokator'] + argstring.split(),
                             standalone_mode=False)

    @click.group()
    @click.pass_obj
    def click_invokator(self):
        pass


# Let's toss this and use click instead.
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

    def __init__(self, common_lock: threading.RLock | None = None) -> None:
        self.SERVER_LOCK = common_lock
        self.TCP_CALLS = {'test': self.sample_locked_func}

    def invoke_call(self, cmd: str) -> str:
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

    def help_string(self) -> str:
        return self.DOCOPTSTR

    @classmethod
    def main(cls):
        '''
        This turns this class into a shell-invokable.
        On the conditions that it is bound to an entrypoint in pyproject.toml
        '''
        import sys
        instance = cls()
        print(' '.join(sys.argv[1:]))
        return instance.invoke_call(' '.join(sys.argv[1:]))

    def set_lock_obj(self, lock: threading.RLock) -> None:
        self.SERVER_LOCK = lock

    @locking_func_decorator
    def sample_locked_func(self) -> str:
        import time
        time.sleep(1.0)
        return "OK."
