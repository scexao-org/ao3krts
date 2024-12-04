'''
    First batch of commands for g2if!
'''

from __future__ import annotations

import typing as typ

import logging

logg = logging.getLogger(__name__)

from .dispatcher import ClickDispatcher, ClickRemotelyInvokableObject, FLT_OK

import click

from ..control.dm import TTManager, DM3kManager, WTTManager
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
    @staticmethod
    def flat() -> str:
        DM3kCommand.CALLEE.flat()
        return f''

    @DISPATCHER.click_invokator.command('saveflat0')
    def saveflat0() -> str:
        DM3kCommand.CALLEE.save_0_to_flat()
        return f''

    @DISPATCHER.click_invokator.command('saveflatagg')
    def saveflatagg() -> str:
        DM3kCommand.CALLEE.save_agg_to_flat()
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
    @staticmethod
    def zero() -> str:
        TTCommand.CALLEE.zero()
        return f''

    @DISPATCHER.click_invokator.command('flat')
    @staticmethod
    def flat() -> str:
        TTCommand.CALLEE.flat()
        return f''

    @DISPATCHER.click_invokator.command('saveflat0')
    @staticmethod
    def saveflat0() -> str:
        TTCommand.CALLEE.save_0_to_flat()
        return f''

    @DISPATCHER.click_invokator.command('saveflatagg')
    @staticmethod
    def saveflatagg() -> str:
        TTCommand.CALLEE.save_agg_to_flat()
        return f''

    @DISPATCHER.click_invokator.command('x', context_settings=FLT_OK)
    @click.option('-n', '--nudge', is_flag=True)
    @click.argument('x', type=float)
    @click.argument('chan', type=int, default=0)
    @staticmethod
    def xset(x: float, chan: int, nudge: bool) -> str:
        if nudge:
            TTCommand.CALLEE.xnudge(x, chan=chan)
        else:
            TTCommand.CALLEE.xset(x, chan=chan)
        return f'{x=}, {chan=}'

    @DISPATCHER.click_invokator.command('y', context_settings=FLT_OK)
    @click.option('-n', '--nudge', is_flag=True)
    @click.argument('y', type=float)
    @click.argument('chan', type=int, default=0)
    @staticmethod
    def yset(y: float, chan: int, nudge: bool) -> str:
        if nudge:
            TTCommand.CALLEE.ynudge(y, chan=chan)
        else:
            TTCommand.CALLEE.yset(y, chan=chan)
        return f'{y=}, {chan=}'

    @DISPATCHER.click_invokator.command('xy', context_settings=FLT_OK)
    @click.option('-n', '--nudge', is_flag=True)
    @click.argument('x', type=float)
    @click.argument('y', type=float)
    @click.argument('chan', type=int, default=0)
    @staticmethod
    def set(x: float, y: float, chan: int, nudge: bool) -> str:
        if nudge:
            TTCommand.CALLEE.nudge(x, y, chan=chan)
        else:
            TTCommand.CALLEE.set(x, y, chan=chan)
        return f'{x=}, {y=}, {chan=}'


class WTTCommand(ClickRemotelyInvokableObject):
    NAME = 'WTT'
    DESCR = 'WTT Control'

    DISPATCHER = ClickDispatcher(click_group=NAME)
    CALLEE = WTTManager()

    # TODO: optional args not click'd yet
    @DISPATCHER.click_invokator.command('zero')
    @staticmethod
    def zero() -> str:
        WTTCommand.CALLEE.zero()
        return f''

    @DISPATCHER.click_invokator.command('x', context_settings=FLT_OK)
    @click.option('-n', '--nudge', is_flag=True)
    @click.argument('x', type=float)
    @staticmethod
    def xset(x: float, nudge: bool) -> str:
        if nudge:
            WTTCommand.CALLEE.xnudge(x)
        else:
            WTTCommand.CALLEE.xset(x)
        return f'{x=}'

    @DISPATCHER.click_invokator.command('y', context_settings=FLT_OK)
    @click.option('-n', '--nudge', is_flag=True)
    @click.argument('y', type=float)
    @staticmethod
    def yset(y: float, chan: int, nudge: bool) -> str:
        if nudge:
            WTTCommand.CALLEE.ynudge(y)
        else:
            WTTCommand.CALLEE.yset(y)
        return f'{y=}, {chan=}'

    @DISPATCHER.click_invokator.command('xy', context_settings=FLT_OK)
    @click.option('-n', '--nudge', is_flag=True)
    @click.argument('x', type=float)
    @click.argument('y', type=float)
    @staticmethod
    def set(x: float, y: float, nudge: bool) -> str:
        if nudge:
            WTTCommand.CALLEE.nudge(x, y)
        else:
            WTTCommand.CALLEE.set(x, y)
        return f'{x=}, {y=}'


class StatusCommand(ClickRemotelyInvokableObject):
    NAME = 'STATUS'
    DESCR = 'RTS status report'

    DISPATCHER = ClickDispatcher(click_group=NAME)
    CALLEE = StatusObj()

    @DISPATCHER.click_invokator.command('gen2')
    @click.pass_obj
    def report(self) -> str:
        return StatusCommand.CALLEE.status_report()
