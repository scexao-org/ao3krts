'''
    First batch of commands for g2if!
'''

from __future__ import annotations

import typing as typ

import logging

logg = logging.getLogger(__name__)

from .dispatcher import ClickDispatcher, ClickRemotelyInvokableObject

import click

from ..control.dm import TTManager, DM3kManager
from ..control.status import StatusObj

from hwmain.alpao64.alpao_hkl import AlpaoHKL


class DM3kCommand(ClickRemotelyInvokableObject, DM3kManager):
    NAME = 'DM'
    DESCR = 'DM3k Control'

    DISPATCHER = ClickDispatcher(click_group=NAME)
    CALLEE = DM3kManager()

    @DISPATCHER.click_invokator.command('zero')
    @click.pass_obj
    def zero(self) -> str:
        # self is set to None by click...
        # So we can't use self
        # So this doesnt really need to be a class at all...

        # super().zero() # <-- doesn't work for a lack of self
        # DM3kManager.zero(self) # <-- doesn't work for a lack of self
        DM3kCommand.CALLEE.zero()
        return f''

    # TODO: optional args not click'd yet
    @DISPATCHER.click_invokator.command('flat')
    @click.pass_obj
    def flat(self) -> str:
        DM3kCommand.CALLEE.flat()
        return f''


class DM3kHKLCommand(ClickRemotelyInvokableObject, AlpaoHKL):
    NAME = 'DMC'
    DESCR = 'DM3k HKL'

    DISPATCHER = ClickDispatcher(click_group=NAME)
    CALLEE = AlpaoHKL()

    @DISPATCHER.click_invokator.command('power')
    @click.argument('on_or_off', type=click.Choice(['on', 'off']))
    @click.pass_obj
    def power(self, on_or_off: str) -> str:

        if on_or_off.upper() == 'ON':
            DM3kHKLCommand.CALLEE.poweron()
        else:
            DM3kHKLCommand.CALLEE.poweroff()

        return f''

    @DISPATCHER.click_invokator.command('ack')
    @click.pass_obj
    def error_ack(self, ) -> str:
        DM3kHKLCommand.CALLEE.error_ack()
        return f''

    @DISPATCHER.click_invokator.command('st')
    @click.pass_obj
    def status(self, ) -> str:
        return ','.join(DM3kHKLCommand.CALLEE.state())

    @DISPATCHER.click_invokator.command('rtemp')
    @click.pass_obj
    def rack_temp(self, ) -> str:
        return ','.join([f'{x:.1f}' for x in DM3kHKLCommand.CALLEE.de_temp()])

    @DISPATCHER.click_invokator.command('dmtemp')
    @click.pass_obj
    def dm_temp(self, ) -> str:
        # dm temp
        return '[Probably wrong values]' + ','.join(
                [f'{x:.1f}' for x in DM3kHKLCommand.CALLEE.dm_temp()])


class TTCommand(ClickRemotelyInvokableObject):
    NAME = 'TT'
    DESCR = 'TT Control'

    DISPATCHER = ClickDispatcher(click_group=NAME)
    CALLEE = TTManager()

    # TODO: optional args not click'd yet
    @DISPATCHER.click_invokator.command('zero')
    @click.pass_obj
    def zero(self) -> str:
        TTCommand.CALLEE.zero()
        return f''


class StatusCommand(ClickRemotelyInvokableObject):
    NAME = 'STATUS'
    DESCR = 'RTS status report'

    DISPATCHER = ClickDispatcher(click_group=NAME)
    CALLEE = StatusObj()

    @DISPATCHER.click_invokator.command('gen2')
    @click.pass_obj
    def report(self) -> str:
        return StatusCommand.CALLEE.status_report()
