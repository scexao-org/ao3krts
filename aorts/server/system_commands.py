'''
    First batch of commands for g2if!
'''

from __future__ import annotations

import typing as typ

import logging

logg = logging.getLogger(__name__)

from .dispatcher import ClickDispatcher, ClickRemotelyInvokableObject

import click

from ..toplevel.base_module_modes import RTS_MODULE_ENUM
from ..toplevel.rts_modeselect_obj import RTSModeSwitcher

# TODO move to a ssh util file in swmain.
'rts23-nirwfs'
'pass-through'


class ModeSwitcher(ClickRemotelyInvokableObject):
    NAME = 'MODES'
    DESCR = 'Switch RTS configurations'
    # If we ever want that as a "main", will that work?
    # But then again, we'll favor Pyro, and not care.
    DISPATCHER = ClickDispatcher(click_group=NAME)
    INVOKATOR = DISPATCHER.click_invokator
    # CALLEE... there's no callee cuz there's no parent object with the same features?
    # Here I'm just copy-pasting code like a moron. Could do better.

    CALLEE = RTSModeSwitcher()

    @INVOKATOR.command('test')
    @staticmethod
    def test() -> str:
        print('YO DAT TEST WUT.')
        ModeSwitcher.CALLEE.some_method()
        return f'asdfasdf'

    @INVOKATOR.command('startmodule')
    @click.argument(
            '_module', type=click.Choice(RTS_MODULE_ENUM._member_names_,
                                         case_sensitive=False))
    @staticmethod
    def module_start_command(_module: str):
        module_tag = RTS_MODULE_ENUM(_module.upper())
        print(f'WTF WTF are we calling module start command for {module_tag}??')
        ModeSwitcher.CALLEE.module_start_command(module_tag)

    @INVOKATOR.command('stopmodule')
    @click.argument(
            '_module', type=click.Choice(RTS_MODULE_ENUM._member_names_,
                                         case_sensitive=False))
    @staticmethod
    def module_stop_command(_module: str):
        module_tag = RTS_MODULE_ENUM(_module.upper())
        ModeSwitcher.CALLEE.module_stop_command(module_tag)

    @INVOKATOR.group('switch')
    @staticmethod
    def group_switch() -> None:
        pass

    @group_switch.command('nir')
    @staticmethod
    def nir() -> int:
        ModeSwitcher.CALLEE.switch_pt_to_nir()
        return 0  # Returning an int will cause the dispatcher to capture stdout

    @group_switch.command('pt')
    @staticmethod
    def pt() -> int:
        ModeSwitcher.CALLEE.switch_nir_to_pt()
        return 0  # Returning an int will cause the dispatcher to capture stdout

    @INVOKATOR.command('query')
    @staticmethod
    def query() -> int:
        ModeSwitcher.CALLEE.query()
        return 0  # Returning an int will cause the dispatcher to capture stdout
