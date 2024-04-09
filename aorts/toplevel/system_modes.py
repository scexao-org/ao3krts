from __future__ import annotations

import typing as typ

# We're gonna need a setup and a teardown for all the modes defined
# in config.AORTS_MODES
from .common import AORTS_MODES, MacroRetcode, T_RetCodeMessage


def main_startmode(mode: AORTS_MODES, auto_teardown: bool = False):

    if auto_teardown:
        main_teardown_current_mode()

    # dispatch
    STARTUP_DISPATCH = {}
    # Mode MUST be None

    # Set mode to unknown

    # Set mode to final value

    pass


def main_teardown_current_mode():
    # dispatch
    current_system_mode = AORTS_MODES.read_rtsmode()

    # mode must not be TEST, UNKNOWN, NONE

    TEARDOWN_DISPATCH = {}
    pass
