'''
A simple ad-hoc server class

Multiple objects can be registered, and the dispatching is performed based on the first argument.

Each object is expected to implement the protocol, and use its tcp_dispatch function,
possibly to dispatch the command to a given function call
'''
from __future__ import annotations

import abc
import click

import typing as typ
import threading

import logging

logg = logging.getLogger(__name__)

from swmain.network.tcpserver import InvokableObjectForServer


@click.group
def global_click_invokator(self):
    pass


class ClickDispatcher:

    def __init__(self, click_group: str):
        super().__init__()
        '''
            Turn into a click group bound to the passed name.
        '''
        self.click_group = click_group
        self.click_invokator = global_click_invokator.group(
                click_group.lower())(self._click_invokator)

    def click_dispatch(self, argstring: str) -> str:
        logg.debug(f'invoke_call @ "{self.click_group} {argstring}"')
        '''
        --help causes click to print the help and raise Exit(0)
        Preventing me to return the help in a string!
        Thus, I'll forcefully insert a usageerror
        '''
        import io
        from contextlib import redirect_stdout

        with io.StringIO() as buf, redirect_stdout(buf):
            print('redirected')
            output = buf.getvalue()

        with io.StringIO() as buf, redirect_stdout(buf):
            ret = None
            try:
                ret = self.click_invokator(argstring.split(),
                                           standalone_mode=False,
                                           prog_name=self.click_group.lower())
            except click.exceptions.UsageError as exc:
                assert exc.ctx
                return str(exc) + '\n' + exc.ctx.get_help() + '\n'
            finally:
                captured = buf.getvalue()

        if ret is None or isinstance(ret, int):
            logg.debug(
                    f'{self.click_group.lower()} returned retcode {ret} -- run test help'
            )
            return captured
        else:
            return ret

    def _click_invokator(self):
        pass


class ClickRemotelyInvokableObject(InvokableObjectForServer):

    NAME = 'TEST'
    DESCR = 'Test Object'

    DISPATCHER = ClickDispatcher(click_group=NAME)

    def invoke_call(self, argstring: str) -> str:
        return self.DISPATCHER.click_dispatch(argstring)
