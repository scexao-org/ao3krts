from __future__ import annotations

import os

import typing as typ

from enum import Enum, IntEnum

FILE_RTSMODE = '/tmp/RTS_CURRENTMODE.txt'


class RTS_MODE(str, Enum):
    TEST = 'TEST'
    UNKNOWN = 'UNKNOWN'
    NONE = 'NONE'
    NIR188 = 'NIR_188'
    NIR3K = 'NIR_3K'
    CWFS_NGS188 = 'CWFS_NGS_188'
    CWFS_NGS3K = 'CWFS_NGS_3K'
    PT188 = 'PT_188'
    PT3K = 'PT_3K'

    @classmethod
    def _missing_(cls, value: str) -> RTS_MODE:
        return cls.UNKNOWN

    @classmethod
    def write_rtsmode(cls, mode: RTS_MODE):
        with open(FILE_RTSMODE, 'w') as f:
            f.write(mode.value + '\n')

    @classmethod
    def read_rtsmode(cls) -> RTS_MODE:
        if not os.path.isfile(FILE_RTSMODE):
            return RTS_MODE.NONE

        with open(FILE_RTSMODE, 'r') as f:
            return RTS_MODE(f.readline().strip())


class MacroRetcode(IntEnum):
    SUCCESS = 0
    FAILURE = 1


if typ.TYPE_CHECKING:
    T_RetCodeMessage: typ.TypeAlias = tuple[MacroRetcode, str]
    T_MacroFunction: typ.TypeAlias = typ.Callable[[], T_RetCodeMessage]
    T_StartStopPair: typ.TypeAlias = tuple[T_MacroFunction, T_MacroFunction]
