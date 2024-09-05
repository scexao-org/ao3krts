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
    @click.pass_obj
    def efgh(self, x: int) -> str:
        return f'efgh: {x} -> {x+1}'


if __name__ == "__main__":
    from swmain.infra.logger import init_logger_autoname
    init_logger_autoname()
    logg = logging.getLogger()
    logg.setLevel(logging.INFO)
    for h in logg.handlers:
        h.setLevel(logging.INFO)
    x = ActualInterestingTestObject()

    print('--------------\n', x.DISPATCHER.click_dispatch('--help'),
          '\n--------------')
    print('--------------\n', x.DISPATCHER.click_dispatch('efgh --help'),
          '\n--------------')
    print('--------------\n', x.DISPATCHER.click_dispatch('xsw'),
          '\n--------------')
    print('--------------\n', x.DISPATCHER.click_dispatch('efgh safd'),
          '\n--------------')
