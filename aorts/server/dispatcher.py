'''
A simple ad-hoc server class

Multiple objects can be registered, and the dispatching is performed based on the first argument.

Each object is expected to implement the protocol, and use its tcp_dispatch function,
possibly to dispatch the command to a given function call
'''
from __future__ import annotations

import click

import typing as typ

import logging

logg = logging.getLogger(__name__)

from swmain.network.tcpserver import InvokableObjectForServer

# pass this as context_settings to click commands that need to accept (negative) floats
FLT_OK = {"ignore_unknown_options": True}


@click.group
def global_click_invokator(self):
    pass


def recursive_help(cmd, parent=None):
    ctx = click.core.Context(cmd, info_name=cmd.name, parent=parent)
    print(cmd.get_help(ctx))
    print()
    commands = getattr(cmd, 'commands', {})
    for sub in commands.values():
        recursive_help(sub, ctx)


class ClickDispatcher:

    def __init__(self, click_group: str):
        super().__init__()
        '''
            Turn into a click group bound to the passed name.
        '''
        self.click_group = click_group
        self.click_invokator = global_click_invokator.group(
                click_group.lower())(self._click_invokator)
        self.klass = None

        def recursive_help_caller():
            recursive_help(self.click_invokator)

        self.recursive_helper = self.click_invokator.command('morehelp')(
                recursive_help_caller)

    def set_klass(self, klass):
        self.klass = klass

    def _click_invokator(self):
        # Just a placeholder instance method.
        if self.klass:
            ctx = click.get_current_context()
            # This enables the decorator pass_obj on command classes
            # to pass the class as the 1st argument and make everything behave as a classmethod.
            ctx.obj = self.klass

    def click_dispatch_remote_calls(self, arg_list: str | list[str]) -> str:
        logg.debug(f'invoke_remote_call @ "{self.click_group} {arg_list}"')
        '''
        --help causes click to print the help and raise Exit(0)
        Preventing me to return the help in a string!
        Thus, I'll forcefully insert a usageerror
        '''
        if isinstance(arg_list, str):
            arg_list = arg_list.split()

        import io
        from contextlib import redirect_stdout

        with io.StringIO() as buf, redirect_stdout(buf):
            ret = None
            try:
                ret = self.click_invokator(arg_list, standalone_mode=False,
                                           prog_name=self.click_group.lower())
            except click.exceptions.UsageError as exc:
                assert exc.ctx
                return str(exc) + '\n' + exc.ctx.get_help() + '\n'
            except Exception as exc:
                captured = buf.getvalue()
                return captured + '\n' + f'Exception {type(exc)}: ' + str(
                        exc) + '\n'

            captured = buf.getvalue()

        if ret is None or isinstance(ret, int):
            logg.debug(
                    f'{self.click_group.lower()} returned retcode {ret} -- run test help'
            )
            return captured
        else:
            return ret

    def click_dispatch_cli_calls(self, arg_list: str | list[str]) -> typ.Any:
        logg.debug(f'invoke_cli_call @ "{self.click_group} {arg_list}"')

        if isinstance(arg_list, str):
            arg_list = arg_list.split()

        return self.click_invokator(arg_list, standalone_mode=False,
                                    prog_name=self.click_group.lower())


class ClickRemotelyInvokableObject(InvokableObjectForServer):

    NAME = 'TEST'
    DESCR = 'Test Object'

    DISPATCHER = ClickDispatcher(click_group=NAME)

    def __init__(self):
        type(self).DISPATCHER.set_klass(type(
                self))  # can I have this invoked at import time?? Probs not!
        self.DISPATCHER.set_klass(self)

    def invoke_call(self, argstring: str) -> str:
        return self.DISPATCHER.click_dispatch_remote_calls(argstring)

    def help_string(self) -> str:
        '''
        Using this mandated abstract function to generate click recursive help.
        '''
        return self.DISPATCHER.click_dispatch_remote_calls('morehelp')
