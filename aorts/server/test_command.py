from __future__ import annotations

import typing as typ

import logging

logg = logging.getLogger(__name__)

from .dispatcher import ClickDispatcher, ClickRemotelyInvokableObject

import click


class ActualInterestingTestObject(ClickRemotelyInvokableObject):

    NAME = 'TEST'
    DESCR = 'Test Object'

    DISPATCHER = ClickDispatcher(click_group=NAME)

    @DISPATCHER.click_invokator.command('efgh')
    @click.argument('x', type=int)
    @staticmethod
    def efgh(x: int) -> str:
        return f'efgh: {x} -> {x+1}'


if __name__ == "__main__":
    from swmain.infra.logger import init_logger_autoname
    init_logger_autoname()
    logg = logging.getLogger()
    logg.setLevel(logging.INFO)
    for h in logg.handlers:
        h.setLevel(logging.INFO)
    x = ActualInterestingTestObject()

    print('--------------\n',
          x.DISPATCHER.click_dispatch_remote_calls('--help'),
          '\n--------------')
    '''
 Usage: test [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  efgh
    '''
    print('--------------\n',
          x.DISPATCHER.click_dispatch_remote_calls('efgh --help'),
          '\n--------------')
    '''
 Usage: test efgh [OPTIONS] X

Options:
  --help  Show this message and exit.

    '''
    print('--------------\n', x.DISPATCHER.click_dispatch_remote_calls('xsw'),
          '\n--------------')
    '''
 No such command 'xsw'.
Usage: test [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  efgh
    '''
    print('--------------\n',
          x.DISPATCHER.click_dispatch_remote_calls('efgh safd'),
          '\n--------------')
    '''
 'safd' is not a valid integer.
Usage: test efgh [OPTIONS] X

Options:
  --help  Show this message and exit.

    '''
    print('--------------\n',
          x.DISPATCHER.click_dispatch_remote_calls('efgh 33'),
          '\n--------------')
    '''
efgh: 33 -> 34
    '''
