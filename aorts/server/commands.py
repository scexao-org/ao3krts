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
from ..control.loop import AO3kNIRLoopObject
from ..control.status import StatusObj

from hwmain.alpao64.alpao_hkl import AlpaoHKL


class DM3k(ClickRemotelyInvokableObject, DM3kManager):
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
        DM3k.CALLEE.zero()
        return f''

    # TODO: optional args not click'd yet
    @DISPATCHER.click_invokator.command('flat')
    @click.pass_obj
    def flat(self) -> str:
        DM3k.CALLEE.flat()
        return f''


class DM3kHKL(ClickRemotelyInvokableObject, AlpaoHKL):
    NAME = 'DMC'
    DESCR = 'DM3k HKL'

    DISPATCHER = ClickDispatcher(click_group=NAME)
    CALLEE = AlpaoHKL()

    @DISPATCHER.click_invokator.command('power')
    @click.argument('on_or_off', type=click.Choice(['on', 'off']))
    @click.pass_obj
    def power(self, on_or_off: str) -> str:

        if on_or_off.upper() == 'ON':
            DM3kHKL.CALLEE.poweron()
        else:
            DM3kHKL.CALLEE.poweroff()

        return f''

    @DISPATCHER.click_invokator.command('ack')
    @click.pass_obj
    def error_ack(self, ) -> str:
        DM3kHKL.CALLEE.error_ack()
        return f''

    @DISPATCHER.click_invokator.command('st')
    @click.pass_obj
    def status(self, ) -> str:
        return ','.join(DM3kHKL.CALLEE.state())

    @DISPATCHER.click_invokator.command('rtemp')
    @click.pass_obj
    def rack_temp(self, ) -> str:
        return ','.join([f'{x:.1f}' for x in DM3kHKL.CALLEE.de_temp()])

    @DISPATCHER.click_invokator.command('dmtemp')
    @click.pass_obj
    def dm_temp(self, ) -> str:
        # dm temp
        return '[Probably wrong values]' + ','.join(
                [f'{x:.1f}' for x in DM3kHKL.CALLEE.dm_temp()])


class TT(ClickRemotelyInvokableObject):
    NAME = 'TT'
    DESCR = 'TT Control'

    DISPATCHER = ClickDispatcher(click_group=NAME)
    CALLEE = TTManager()

    # TODO: optional args not click'd yet
    @DISPATCHER.click_invokator.command('zero')
    @click.pass_obj
    def zero(self) -> str:
        TT.CALLEE.zero()
        return f''


class Loop(ClickRemotelyInvokableObject):
    NAME = 'LOOP'
    DESCR = 'Loop on/off'
    # If we ever want that as a "main", will that work?
    # But then again, we'll favor Pyro, and not care.
    DISPATCHER = ClickDispatcher(click_group=NAME)
    CALLEE = AO3kNIRLoopObject()

    @DISPATCHER.click_invokator.command('on')
    @click.pass_obj
    def on(self):
        Loop.CALLEE.loop_close()

    @DISPATCHER.click_invokator.command('off')
    @click.pass_obj
    def off(self):
        Loop.CALLEE.loop_open()


class Gain(ClickRemotelyInvokableObject):
    NAME = 'GAIN'
    DESCR = 'Gain set: dmg, ttg'
    DISPATCHER = ClickDispatcher(click_group=NAME)
    CALLEE = Loop.CALLEE

    @DISPATCHER.click_invokator.command('dmg')
    @click.argument('gain', type=float)
    @click.pass_obj
    def dm_gain(self, gain: float):
        Loop.CALLEE.set_dmgain(gain)

    @DISPATCHER.click_invokator.command('ttg')
    @click.argument('gain', type=float)
    @click.pass_obj
    def tt_gain(self, gain: float):
        Loop.CALLEE.set_ttgain(gain)


class Status(ClickRemotelyInvokableObject):
    NAME = 'STATUS'
    DESCR = 'RTS status report'

    DISPATCHER = ClickDispatcher(click_group=NAME)
    CALLEE = StatusObj()

    @DISPATCHER.click_invokator.command('gen2')
    @click.pass_obj
    def report(self) -> str:
        return Status.CALLEE.status_report()
