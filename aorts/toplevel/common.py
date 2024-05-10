from __future__ import annotations

import os

import typing as typ

from enum import Enum, IntEnum

FILE_RTSMODE = '/tmp/RTS_CURRENTMODE.txt'


class MacroRetcode(IntEnum):
    SUCCESS = 0
    FAILURE = 1


if typ.TYPE_CHECKING:
    T_RetCodeMessage: typ.TypeAlias = tuple[MacroRetcode, str]
    T_MacroFunction: typ.TypeAlias = typ.Callable[[], T_RetCodeMessage]
    T_StartStopPair: typ.TypeAlias = tuple[T_MacroFunction, T_MacroFunction]


class RTS_MODULE(str, Enum):
    # Note: for the click parser, left and right DO need to match
    IIWI = 'IIWI'
    DAC40 = 'DAC40'
    APD = 'APD'
    PT_APD = 'PT_APD'
    PT_DAC = 'PT_DAC'
    DM3K = 'DM3K'

    def register_startup_function(self,
                                  func: T_MacroFunction) -> T_MacroFunction:

        if not hasattr(RTS_MODULE, 'START_FUNC_DICT'):
            RTS_MODULE.START_FUNC_DICT: dict[RTS_MODULE, T_MacroFunction] = {}

        if self in RTS_MODULE.START_FUNC_DICT:
            raise ValueError(
                    f'Double register of RTS_MODULE startup function for {self}'
            )

        RTS_MODULE.START_FUNC_DICT[self] = func

        return func

    def register_stop_function(self, func: T_MacroFunction) -> T_MacroFunction:

        if not hasattr(RTS_MODULE, 'STOP_FUNC_DICT'):
            RTS_MODULE.STOP_FUNC_DICT: dict[RTS_MODULE, T_MacroFunction] = {}

        if self in RTS_MODULE.STOP_FUNC_DICT:
            raise ValueError(
                    f'Double register of RTS_MODULE stop function for {self}')

        RTS_MODULE.STOP_FUNC_DICT[self] = func

        return func


class RTS_MODE(str, Enum):
    # Note: for the click parser, left and right DO need to match
    TEST = 'TEST'
    UNKNOWN = 'UNKNOWN'
    NONE = 'NONE'
    NIR188 = 'NIR188'
    NIR3K = 'NIR3K'
    CWFS_NGS188 = 'CWFS_NGS188'
    CWFS_NGS3K = 'CWFS_NGS3K'
    PT188 = 'PT188'
    PT3K = 'PT3K'

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
