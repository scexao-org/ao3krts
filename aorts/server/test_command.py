from __future__ import annotations

import typing as typ

import logging

logg = logging.getLogger(__name__)

from .dispatcher import ClickDispatcher, ClickRemotelyInvokableObject, FLT_OK

import click


class ActualInterestingTestObject(ClickRemotelyInvokableObject):

    NAME = 'TEST'
    DESCR = 'Test Object'

    DISPATCHER = ClickDispatcher(click_group=NAME)

    A_CLASS_ATTR_FOR_TESTING = [1, 2, 3, 4, 5, 6]

    @DISPATCHER.click_invokator.command('efgh')
    @click.argument('x', type=int)
    @staticmethod
    def efgh(x: int) -> str:
        return f'efgh: {x} -> {x+1}'

    @DISPATCHER.click_invokator.command('raises')
    @staticmethod
    def raises():
        print('Raising an error as expected [print message]'
              )  # Should show in the client return
        logg.error('Raising an error as expected [log message]'
                   )  # Should show in the log.
        raise ValueError('Raising an error as expected [error message]'
                         )  # Should show in the client return
        return 'Raising an error as expected [return message]'  # Shouldn't.

    @DISPATCHER.click_invokator.command('x', context_settings=FLT_OK)
    @click.argument('x', type=float)
    @click.argument('chan', type=int, default=0)
    @staticmethod
    def setx(x: float, chan: int) -> str:
        return f'{x=}, {chan=}'

    @DISPATCHER.click_invokator.command('y', context_settings=FLT_OK)
    @click.option('-n', '--nudge', is_flag=True)
    @click.argument('y', type=float)
    @click.argument('chan', type=int, default=0)
    @staticmethod
    def sety(y: float, chan: int, nudge: bool) -> str:
        return f'{y=}, {chan=} {nudge=}'

    @DISPATCHER.click_invokator.command('set', context_settings=FLT_OK)
    @click.argument('x', type=float)
    @click.argument('y', type=float)
    @click.argument('chan', type=int, default=0)
    @staticmethod
    def set(x: float, y: float, chan: int) -> str:
        return f'{x=}, {y=}, {chan=}'

    @DISPATCHER.click_invokator.command('cls')
    @click.pass_obj
    def classmthd(cls):
        print(cls.A_CLASS_ATTR_FOR_TESTING[0])
        print(cls)
        return 0

    #@classmethod


if __name__ == "__main__":
    import sys
    x = ActualInterestingTestObject()
    print(x.DISPATCHER.click_dispatch_cli_calls(sys.argv[1:]))

    sys.exit()

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
