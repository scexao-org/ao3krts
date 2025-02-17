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
from ..control.wtt_offloader import WTTOffloaderControl


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
        # Also set WTT off

    @DISPATCHER.click_invokator.command('killall')
    @staticmethod
    def killall():
        LoopCommand.CALLEE.open_all_loops()

    @DISPATCHER.click_invokator.command('wtt')
    @click.argument('_state', type=click.Choice(['on', 'off'],
                                                case_sensitive=False))
    @staticmethod
    def wtt_toggle(_state: str):
        state = _state.lower() == 'on'
        LoopCommand.CALLEE.wtt_toggle(state)

    @DISPATCHER.click_invokator.command('ho')
    @click.argument(
            '_state', type=click.Choice(['on', 'off', 'onnowtt'],
                                        case_sensitive=False))
    @staticmethod
    def holoop_toggle(_state: str):
        if _state == 'on':
            LoopCommand.CALLEE.holoop_toggle(True, True)
        elif _state == 'off':
            LoopCommand.CALLEE.holoop_toggle(False)
        elif _state == 'onnowtt':
            LoopCommand.CALLEE.holoop_toggle(True, False)

    @DISPATCHER.click_invokator.command('lo')
    @click.argument('_state', type=click.Choice(['on', 'off'],
                                                case_sensitive=False))
    @staticmethod
    def loloop_toggle(_state: str):
        state = _state.lower() == 'on'
        LoopCommand.CALLEE.loloop_toggle(state)


class GainCommand(ClickRemotelyInvokableObject):
    NAME = 'GAIN'
    DESCR = 'Gain set: dmg, ttg, LGS gains/flags'
    DISPATCHER = ClickDispatcher(click_group=NAME)
    CALLEE = LoopCommand.CALLEE

    @DISPATCHER.click_invokator.command('dmg')
    @click.argument('gain', type=float)
    @click.pass_obj
    def dm_gain(self, gain: float):
        LoopCommand.CALLEE.set_dm_gain(gain)

    @DISPATCHER.click_invokator.command('ttg')
    @click.argument('gain', type=float)
    @click.pass_obj
    def tt_gain(self, gain: float):
        LoopCommand.CALLEE.set_tt_gain(gain)

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

    @DISPATCHER.click_invokator.command('clear')
    @staticmethod
    def clear():
        LoopCommand.CALLEE.gain_clear()


# Focus offloader is obsolete? Probably; we rather need to report in status gen2 the correct values!
class WTTOffloaderCommand(ClickRemotelyInvokableObject):
    NAME = 'wttl'
    DESCR = 'Control WTT offloader loop'
    DISPATCHER = ClickDispatcher(click_group=NAME)
    CALLEE = WTTOffloaderControl()

    @DISPATCHER.click_invokator.command('on')
    @staticmethod
    def loop_on():
        WTTOffloaderCommand.CALLEE.loop_close()

    @DISPATCHER.click_invokator.command('off')
    @staticmethod
    def loop_off():
        WTTOffloaderCommand.CALLEE.loop_open()

    @DISPATCHER.click_invokator.command('zero')
    @staticmethod
    def reset():
        WTTOffloaderCommand.CALLEE.reset()

    @DISPATCHER.click_invokator.command('gain')
    @click.argument('gain', type=float)
    @staticmethod
    def set_gain(gain: float):
        WTTOffloaderCommand.CALLEE.set_gain(gain)

    @DISPATCHER.click_invokator.command('mult')
    @click.argument('mult', type=float)
    @staticmethod
    def set_leak(mult: float):
        WTTOffloaderCommand.CALLEE.set_mult(mult)

    @DISPATCHER.click_invokator.command('limit')
    @click.argument('limit', type=float)
    @staticmethod
    def set_limit(limit: float):
        WTTOffloaderCommand.CALLEE.set_limit(limit)
