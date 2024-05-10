from __future__ import annotations

import typing as typ

from .common import RTS_MODULE, RTS_MODE
from . import common

from . import module_macros as smac
# from . import cacao_macros as cmac # TODO
'''
STARTUP_PAIRS: dict[RTS_MODULE, common.T_StartStopPair] = {
    RTS_MODULE.IIWI: (smac.iiwi_startup, smac.iiwi_teardown),
    RTS_MODULE.DAC40: (smac.dac40_startup, smac.dac40_teardown),
    RTS_MODULE.APD: (smac.apd_startup, smac.apd_teardown),
    RTS_MODULE.PT_APD: (smac.pt_apd_startup, smac.pt_apd_teardown),
    RTS_MODULE.PT_DAC: (smac.pt_dac_startup, smac.pt_dac_teardown),
}

STARTERS: dict[RTS_MODE, list[common.T_StartStopPair]] = {
        RTS_MODE.NIR188: [
                STARTUP_PAIRS.IIWI,
                STARTUP_PAIRS.DAC40,
                # Cacao stuff
                # Cacao runtime loading stuff
        ],
        RTS_MODE.CWFS_NGS188: [
                STARTUP_PAIRS.APD,
                STARTUP_PAIRS.DAC40,
        ],
        RTS_MODE.PT188: [
                STARTUP_PAIRS.PT_APD,
                STARTUP_PAIRS.PT_DAC,
        ],
}


def get_startup_call_sequence(mode: RTS_MODE
                              ) -> list[common.T_MacroFunction]:
    return [u for u, v in STARTERS[mode]]


def get_teardown_call_sequence(mode: RTS_MODE
                               ) -> list[common.T_MacroFunction]:
    return [v for u, v in STARTERS[mode]][::-1]
'''
