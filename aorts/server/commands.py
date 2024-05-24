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

    @click.command('gen22')
    @click.pass_obj
    def other_report(self) -> str:
        return self.CALLEE.status_report()

    def __init__(self):
        self.DISPATCHER.click_invokator.add_command(self.other_report)
