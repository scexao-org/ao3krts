'''
    First batch of commands for g2if!
'''

from __future__ import annotations

import typing as typ

import logging

logg = logging.getLogger(__name__)

from .dispatcher import ClickDispatcher, ClickRemotelyInvokableObject

import click

from ..control.loop import AO3kNIRLoopObject


class LoopCommand(ClickRemotelyInvokableObject):
    NAME = 'LOOP'
    DESCR = 'Loop on/off'
    # If we ever want that as a "main", will that work?
    # But then again, we'll favor Pyro, and not care.
    DISPATCHER = ClickDispatcher(click_group=NAME)
    CALLEE = AO3kNIRLoopObject()

    @DISPATCHER.click_invokator.command('on')
    @click.pass_obj
    def on(self):
        LoopCommand.CALLEE.loop_close()

    @DISPATCHER.click_invokator.command('off')
    @click.pass_obj
    def off(self):
        LoopCommand.CALLEE.loop_open()


class GainCommand(ClickRemotelyInvokableObject):
    NAME = 'GAIN'
    DESCR = 'Gain set: dmg, ttg'
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
