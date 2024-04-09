from __future__ import annotations

import os

import typing as typ

from enum import Enum, IntEnum

FILE_RTSMODE = '/tmp/RTS_CURRENTMODE.txt'


class AORTS_MODES(str, Enum):
    TEST = 'TEST'
    UNKNOWN = 'UNKNOWN'
    NONE = 'NONE'
    NIR188 = 'NIR_188'
    NIR3K = 'NIR_3K'
    CWFS_NGS_188 = 'CWFS_NGS_188'
    CWFS_NGS_3K = 'CWFS_NGS_3K'
    PT188 = 'PT_188'
    PT3K = 'PT_3K'

    @classmethod
    def _missing_(cls, value: str) -> AORTS_MODES:
        return cls.UNKNOWN

    @classmethod
    def write_rtsmode(cls, mode: AORTS_MODES):
        with open(FILE_RTSMODE, 'w') as f:
            f.write(mode.value + '\n')

    @classmethod
    def read_rtsmode(cls) -> AORTS_MODES:
        if not os.path.isfile(FILE_RTSMODE):
            return AORTS_MODES.NONE

        with open(FILE_RTSMODE, 'r') as f:
            return AORTS_MODES(f.readline().strip())


class MacroRetcode(IntEnum):
    SUCCESS = 0
    FAILURE = 1


if typ.TYPE_CHECKING:
    T_RetCodeMessage: typ.TypeAlias = tuple[MacroRetcode, str]
    T_MacroFunction: typ.TypeAlias = typ.Callable[[None], T_RetCodeMessage]
