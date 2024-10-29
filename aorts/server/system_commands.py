'''
    First batch of commands for g2if!
'''

from __future__ import annotations

import typing as typ

import logging

logg = logging.getLogger(__name__)

from .dispatcher import ClickDispatcher, ClickRemotelyInvokableObject

import click

from ..toplevel import modules
from ..toplevel.rts_modeselect import invoke_sequence_pretty_noninteractive, set_mode_in_obcp, get_mode_from_obcp

# TODO move to a ssh util file in swmain.
'rts23-nirwfs'
'pass-through'


class ModeSwitcher(ClickRemotelyInvokableObject):
    NAME = 'MODESWITCH'
    DESCR = 'Switch RTS configurations'
    # If we ever want that as a "main", will that work?
    # But then again, we'll favor Pyro, and not care.
    DISPATCHER = ClickDispatcher(click_group=NAME)
    # CALLEE... there's no callee cuz there's no parent object with the same features?
    # Here I'm just copy-pasting code like a moron. Could do better.

    @DISPATCHER.click_invokator.command('nir')
    @click.pass_obj
    def nir(self) -> str:
        invoke_sequence_pretty_noninteractive([
                modules.PTAPD_RTSModule.stop_function,
                modules.PTDAC_RTSModule.stop_function,
                modules.DAC40_RTSModule.start_function,
                modules.APD_RTSModule.start_function,
        ])
        set_mode_in_obcp(
                'rts23-nirwfs'
        )  # This is terrible cuz we set the mode in OBCP and RTS at completely different moments.
        return 'nir'
        return STDOUT_SHOULD_BE_CAPTURED  # Maybe as a decorator? capture and return stdout?

    @DISPATCHER.click_invokator.command('pt')
    @click.pass_obj
    def pt(self) -> str:
        invoke_sequence_pretty_noninteractive([
                modules.APD_RTSModule.stop_function,
                modules.DAC40_RTSModule.stop_function,
                modules.PTDAC_RTSModule.start_function,
                modules.PTAPD_RTSModule.start_function,
        ])
        set_mode_in_obcp('pass-through')  # On valide?
        return 'pt'
        return STDOUT_SHOULD_BE_CAPTURED

    @DISPATCHER.click_invokator.command('query')
    @click.pass_obj
    def query(self) -> str:
        obcp_thinks = get_mode_from_obcp()
        from ..toplevel.base_module_modes import RTS_MODE
        rts_thinks = RTS_MODE.read_rtsmode()
        return f'[RTS23 mode] OBCP: {obcp_thinks} - RTS: {rts_thinks}'
