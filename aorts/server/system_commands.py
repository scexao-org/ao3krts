'''
    First batch of commands for g2if!
'''

from __future__ import annotations

import typing as typ

import logging

logg = logging.getLogger(__name__)

from .dispatcher import ClickDispatcher, ClickRemotelyInvokableObject

import click

from ..modules.base_module_modes import RTS_MODULE_ENUM, RTS_MODE_ENUM
from ..modules.rts_modeselect_obj import RTSModeSwitcher

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
        return ModeSwitcher.CALLEE.__str__()

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

    @INVOKATOR.command('confmodule')
    @click.argument(
            '_module', type=click.Choice(RTS_MODULE_ENUM._member_names_,
                                         case_sensitive=False))
    @click.argument(
            '_cfg', type=click.Choice(RTS_MODE_ENUM._member_names_,
                                      case_sensitive=False))
    @staticmethod
    def module_configure_command(_module: str, _cfg: str):
        module_tag = RTS_MODULE_ENUM(_module.upper())
        submode_tag = RTS_MODE_ENUM(_cfg.upper())
        ModeSwitcher.CALLEE.module_configure_command(module_tag, submode_tag)

    @INVOKATOR.command('confstartmodule')
    @click.argument(
            '_module', type=click.Choice(RTS_MODULE_ENUM._member_names_,
                                         case_sensitive=False))
    @click.argument(
            '_cfg', type=click.Choice(RTS_MODE_ENUM._member_names_,
                                      case_sensitive=False))
    @staticmethod
    def module_confstart_command(_module: str, _cfg: str):
        module_tag = RTS_MODULE_ENUM(_module.upper())
        submode_tag = RTS_MODE_ENUM(_cfg.upper())
        ModeSwitcher.CALLEE.module_confstart_command(module_tag, submode_tag)

    @INVOKATOR.command('setmode')
    @click.argument(
            '_mode', type=click.Choice(RTS_MODE_ENUM._member_names_,
                                       case_sensitive=False))
    @staticmethod
    def set_mode(_mode: str):
        mode_tag = RTS_MODE_ENUM(_mode.upper())
        ModeSwitcher.CALLEE.mode_set_command(mode_tag)

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
