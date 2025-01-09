'''
    First batch of commands for g2if!
'''

from __future__ import annotations

import typing as typ

import logging

logg = logging.getLogger(__name__)

from .dispatcher import ClickDispatcher, ClickRemotelyInvokableObject

import click

from ..control.loop import GlobalLoopGainController
from ..control.foc_offloader import FocusLGSOffloader


class LoopCommand(ClickRemotelyInvokableObject):
    NAME = 'LOOP'
    DESCR = 'Loop on/off'
    # If we ever want that as a "main", will that work?
    # But then again, we'll favor Pyro, and not care.
    DISPATCHER = ClickDispatcher(click_group=NAME)
    CALLEE = GlobalLoopGainController()

    # TODO DETECT WHICH RTS MODE AND SEND COMMAND TO NIR OR HOWFS OR LOWFS
    # TODO Probably just bundle multiple callees.

    @DISPATCHER.click_invokator.command('on')
    @staticmethod
    def on():
        LoopCommand.CALLEE.loop_close()

    @DISPATCHER.click_invokator.command('off')
    @staticmethod
    def off():
        LoopCommand.CALLEE.loop_open()

    @DISPATCHER.click_invokator.command('killall')
    @staticmethod
    def killall():
        LoopCommand.CALLEE.open_all_loops()


class GainCommand(ClickRemotelyInvokableObject):
    NAME = 'GAIN'
    DESCR = 'Gain set: dmg, ttg, LGS gains/flags'
    DISPATCHER = ClickDispatcher(click_group=NAME)
    CALLEE = LoopCommand.CALLEE

    @DISPATCHER.click_invokator.command('dmg')
    @click.argument('gain', type=float)
    @click.pass_obj
    def dm_gain(self, gain: float):
        LoopCommand.CALLEE.set_dmgain(gain)

    @DISPATCHER.click_invokator.command('ttg')
    @click.argument('gain', type=float)
    @click.pass_obj
    def tt_gain(self, gain: float):
        LoopCommand.CALLEE.set_ttgain(gain)

    # LGS #
    @DISPATCHER.click_invokator.command('htt')
    @click.argument('flag', type=click.IntRange(0, 1))
    @click.pass_obj
    def htt_flag(self, flag: int):
        LoopCommand.CALLEE.set_htt_flag(bool(flag))

    @DISPATCHER.click_invokator.command('hdf')
    @click.argument('flag', type=click.IntRange(0, 1))
    @click.pass_obj
    def hdf_flag(self, flag: int):
        LoopCommand.CALLEE.set_hdf_flag(bool(flag))

    @DISPATCHER.click_invokator.command('ltt')
    @click.argument('gain', type=float)
    @click.pass_obj
    def ltt_gain(self, gain: float):
        LoopCommand.CALLEE.set_ltt_gain(gain)

    @DISPATCHER.click_invokator.command('ldf')
    @click.argument('gain', type=float)
    @click.pass_obj
    def ldf_gain(self, gain: float):
        LoopCommand.CALLEE.set_ldf_gain(gain)

    @DISPATCHER.click_invokator.command('wtt')
    @click.argument('gain', type=float)
    @click.pass_obj
    def wtt_gain(self, gain: float):
        LoopCommand.CALLEE.set_wtt_gain(gain)


# Focus offloader is obsolete? Probably; we rather need to report in status gen2 the correct values!
class FocusOffloaderCommand(ClickRemotelyInvokableObject):
    NAME = 'FOCOFFL'
    DESCR = 'Focus offloader av. gain'
    DISPATCHER = ClickDispatcher(click_group=NAME)
    CALLEE = FocusLGSOffloader()

    @DISPATCHER.click_invokator.command('ttg')
    @click.argument('avg_gain', type=float)
    @staticmethod
    def set_av_gain(avg_gain: float):
        FocusOffloaderCommand.CALLEE.set_ave_gain(avg_gain)

    @DISPATCHER.click_invokator.command('reset')
    @staticmethod
    def reset():
        FocusOffloaderCommand.CALLEE.reset()
